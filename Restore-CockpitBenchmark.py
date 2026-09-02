#!/usr/bin/env python3
"""Safely restore the cockpit benchmark's independent Git repositories.

The transport is treated as untrusted input.  Every archive is hashed and
structurally inspected before the optional repository selector is applied.
Extraction is manual (``TarFile.extract*`` is intentionally never used), and
no Git command is run until extracted metadata has passed a fail-closed local
configuration and indirection audit.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import types
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Iterable


# A public-clone restore must remain outer-worktree clean while importing the
# sibling verifier; never create an untracked ``__pycache__`` in that wrapper.
sys.dont_write_bytecode = True


TRANSPORT_SCHEMA = "2.0.0"
OID_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
DRIVE_RE = re.compile(r"^[A-Za-z]:")
CONTROL_RE = re.compile(r"[\x00-\x1f]")
MAX_ARCHIVE_MEMBERS = 2_000_000
MAX_ARCHIVE_EXPANDED_BYTES = 16 * 1024 * 1024 * 1024
MAX_CONFIG_BYTES = 4 * 1024 * 1024
WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "CLOCK$",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class RestoreError(RuntimeError):
    """A fail-closed transport or restore validation failure."""


@contextlib.contextmanager
def normal_temporary_directory(*, prefix: str, dir: str | os.PathLike[str] | None = None):
    """Create a private-enough scratch directory without tempfile's Windows ACL bug.

    The Microsoft Store Python build can create an unusable mode-0700 directory
    on some Windows volumes.  A UUID name under an already trusted parent gives
    the needed exclusivity without changing the directory ACL.
    """

    parent = Path(dir) if dir is not None else Path.cwd()
    parent.mkdir(parents=True, exist_ok=True)
    # Keep Windows paths well below the legacy MAX_PATH boundary; the caller's
    # descriptive prefix is intentionally shortened because nested Git hook and
    # object names can add more than 100 characters.
    path = parent / f"{prefix[:4]}{uuid.uuid4().hex[:10]}"
    path.mkdir(exist_ok=False)
    try:
        yield str(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RestoreError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RestoreError(f"cannot read strict JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RestoreError(f"expected JSON object: {path}")
    return value


def sha256_stream(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return sha256_stream(stream)


def canonical_relative(value: Any, label: str) -> tuple[str, tuple[str, ...], str]:
    if not isinstance(value, str) or not value:
        raise RestoreError(f"{label} must be a non-empty string")
    if value != unicodedata.normalize("NFC", value):
        raise RestoreError(f"{label} is not Unicode NFC: {value!r}")
    if "\\" in value:
        raise RestoreError(f"{label} contains a Windows path separator: {value!r}")
    if value.startswith(("/", "//")) or DRIVE_RE.match(value):
        raise RestoreError(f"{label} is absolute, UNC, or drive-qualified: {value!r}")
    parts = tuple(value.split("/"))
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise RestoreError(f"{label} has an empty/dot/traversal component: {value!r}")
    canonical_parts: list[str] = []
    for part in parts:
        if CONTROL_RE.search(part):
            raise RestoreError(f"{label} has a control character: {value!r}")
        if ":" in part:
            raise RestoreError(f"{label} contains a Windows ADS component: {value!r}")
        if part.endswith((" ", ".")):
            raise RestoreError(f"{label} has a trailing space/dot: {value!r}")
        if len(part) > 255:
            raise RestoreError(f"{label} component is too long: {value!r}")
        stem = part.split(".", 1)[0].upper()
        if stem in WINDOWS_RESERVED:
            raise RestoreError(f"{label} contains a Windows reserved name: {value!r}")
        canonical_parts.append(unicodedata.normalize("NFC", part).casefold())
    normalized = "/".join(parts)
    return normalized, parts, "/".join(canonical_parts)


def _is_reparse_or_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def reject_reparse_ancestors(path: Path) -> None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.exists() and _is_reparse_or_link(current):
            raise RestoreError(f"symlink/junction/reparse path is forbidden: {current}")


def contained_target(root: Path, parts: tuple[str, ...], label: str) -> Path:
    reject_reparse_ancestors(root)
    root_resolved = root.resolve(strict=False)
    candidate = root.joinpath(*parts)
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise RestoreError(f"{label} escapes containment root: {candidate}") from exc
    return candidate


def safe_git_environment() -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    environment.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_LFS_SKIP_SMUDGE": "1",
            "GIT_ALLOW_PROTOCOL": "",
            "GIT_PROTOCOL_FROM_USER": "0",
            "GCM_INTERACTIVE": "Never",
        }
    )
    return environment


def run_git(
    repository: Path,
    *arguments: str,
    git_dir: bool = False,
    allowed_return_codes: Iterable[int] = (0,),
) -> tuple[int, str, str]:
    command = [
        "git",
        "--no-optional-locks",
        "-c",
        "maintenance.auto=false",
        "-c",
        "gc.auto=0",
        "-c",
        f"core.hooksPath={os.devnull}",
        "-c",
        "core.fsmonitor=false",
        "-c",
        f"core.attributesFile={os.devnull}",
        "-c",
        f"core.excludesFile={os.devnull}",
        "-c",
        "protocol.allow=never",
        "-c",
        "protocol.file.allow=never",
        "-c",
        "protocol.ext.allow=never",
        "-c",
        "filter.lfs.required=false",
        "-c",
        "filter.lfs.smudge=",
        "-c",
        "filter.lfs.process=",
    ]
    command.extend(["--git-dir", str(repository)] if git_dir else ["-C", str(repository)])
    completed = subprocess.run(
        [*command, *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=safe_git_environment(),
    )
    allowed = set(allowed_return_codes)
    if completed.returncode not in allowed:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RestoreError(
            f"git {' '.join(arguments)} failed in {repository} "
            f"({completed.returncode}): {detail}"
        )
    return completed.returncode, completed.stdout, completed.stderr


def _validate_tar_members(
    members: list[tarfile.TarInfo],
    *,
    archive: Path,
    max_members: int,
    max_expanded_bytes: int,
) -> dict[str, Any]:
    if not members:
        raise RestoreError(f"empty archive: {archive}")
    if len(members) > max_members:
        raise RestoreError(f"archive member quota exceeded: {archive}")
    names: dict[str, tuple[str, str]] = {}
    expanded = 0
    for member in members:
        normalized, parts, key = canonical_relative(member.name.rstrip("/") or member.name, "tar member")
        if parts[0] != ".git":
            raise RestoreError(f"archive member is outside .git: {member.name!r}")
        sparse = getattr(member, "sparse", None)
        sparse_headers = any(name.lower().startswith("gnu.sparse") for name in member.pax_headers)
        if sparse is not None or sparse_headers or member.type == tarfile.GNUTYPE_SPARSE:
            raise RestoreError(f"sparse archive member is forbidden: {member.name!r}")
        if not (member.isdir() or member.isfile()):
            raise RestoreError(f"link/device/special archive member is forbidden: {member.name!r}")
        kind = "directory" if member.isdir() else "file"
        if key in names:
            previous = names[key][0]
            raise RestoreError(
                f"duplicate/casefold/Unicode-colliding archive members: {previous!r}, {member.name!r}"
            )
        names[key] = (member.name, kind)
        if member.size < 0:
            raise RestoreError(f"negative archive member size: {member.name!r}")
        if member.isfile():
            expanded += member.size
            if expanded > max_expanded_bytes:
                raise RestoreError(f"archive expanded-byte quota exceeded: {archive}")
        # Reject file/descendant ambiguity even when a tar omits parent directories.
        parent_parts = key.split("/")
        for length in range(1, len(parent_parts)):
            parent_key = "/".join(parent_parts[:length])
            if parent_key in names and names[parent_key][1] == "file":
                raise RestoreError(f"archive file is also a parent: {names[parent_key][0]!r}")
        if kind == "file":
            prefix = key + "/"
            descendants = [item for item in names if item.startswith(prefix)]
            if descendants:
                raise RestoreError(f"archive file is also a parent: {member.name!r}")
    return {"member_count": len(members), "expanded_bytes": expanded}


def inspect_archive(
    path: Path,
    *,
    expected_sha256: str,
    expected_bytes: int,
    max_members: int = MAX_ARCHIVE_MEMBERS,
    max_expanded_bytes: int = MAX_ARCHIVE_EXPANDED_BYTES,
) -> dict[str, Any]:
    reject_reparse_ancestors(path)
    if _is_reparse_or_link(path) or not path.is_file():
        raise RestoreError(f"archive is not a normal file: {path}")
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        if before.st_size != expected_bytes:
            raise RestoreError(f"archive byte-size mismatch: {path}")
        digest = sha256_stream(stream)
        if digest != expected_sha256:
            raise RestoreError(f"archive SHA-256 mismatch: {path}")
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode="r:") as archive:
            result = _validate_tar_members(
                archive.getmembers(),
                archive=path,
                max_members=max_members,
                max_expanded_bytes=max_expanded_bytes,
            )
        after = os.fstat(stream.fileno())
        stream.seek(0)
        post_digest = sha256_stream(stream)
    identity_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
    if any(getattr(before, field, None) != getattr(after, field, None) for field in identity_fields):
        raise RestoreError(f"archive changed while inspected: {path}")
    if post_digest != digest:
        raise RestoreError(f"archive bytes changed while inspected: {path}")
    return {**result, "sha256": digest, "archive_bytes": before.st_size}


def extract_archive_safely(
    path: Path,
    destination: Path,
    *,
    expected_sha256: str,
    expected_bytes: int,
    max_members: int = MAX_ARCHIVE_MEMBERS,
    max_expanded_bytes: int = MAX_ARCHIVE_EXPANDED_BYTES,
) -> Path:
    if destination.exists():
        raise RestoreError(f"safe extraction destination already exists: {destination}")
    reject_reparse_ancestors(destination.parent)
    destination.mkdir(parents=False, exist_ok=False)
    try:
        with path.open("rb") as stream:
            before = os.fstat(stream.fileno())
            if before.st_size != expected_bytes:
                raise RestoreError(f"archive byte-size mismatch: {path}")
            digest = sha256_stream(stream)
            if digest != expected_sha256:
                raise RestoreError(f"archive SHA-256 mismatch: {path}")
            stream.seek(0)
            with tarfile.open(fileobj=stream, mode="r:") as archive:
                members = archive.getmembers()
                _validate_tar_members(
                    members,
                    archive=path,
                    max_members=max_members,
                    max_expanded_bytes=max_expanded_bytes,
                )
                for member in members:
                    raw_name = member.name.rstrip("/") or member.name
                    _, parts, _ = canonical_relative(raw_name, "tar member")
                    target = contained_target(destination, parts, "tar member target")
                    if member.isdir():
                        target.mkdir(parents=True, exist_ok=True)
                        if _is_reparse_or_link(target):
                            raise RestoreError(f"reparse path appeared during extraction: {target}")
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    reject_reparse_ancestors(target.parent)
                    source = archive.extractfile(member)
                    if source is None:
                        raise RestoreError(f"cannot read archive member: {member.name}")
                    remaining = member.size
                    with source, target.open("xb") as output:
                        while remaining:
                            chunk = source.read(min(1024 * 1024, remaining))
                            if not chunk:
                                raise RestoreError(f"truncated archive member: {member.name}")
                            output.write(chunk)
                            remaining -= len(chunk)
                    if target.stat().st_size != member.size:
                        raise RestoreError(f"extracted member size mismatch: {member.name}")
            after = os.fstat(stream.fileno())
            stream.seek(0)
            post_digest = sha256_stream(stream)
        identity_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
        if any(getattr(before, field, None) != getattr(after, field, None) for field in identity_fields):
            raise RestoreError(f"archive changed while extracted: {path}")
        if post_digest != digest:
            raise RestoreError(f"archive bytes changed while extracted: {path}")
        git_dir = destination / ".git"
        if not git_dir.is_dir() or _is_reparse_or_link(git_dir):
            raise RestoreError(f"archive did not produce a normal .git directory: {path}")
        return git_dir
    except BaseException:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def _read_config_fail_closed(config_path: Path) -> str:
    if not config_path.is_file() or _is_reparse_or_link(config_path):
        raise RestoreError(f"missing or unsafe local Git config: {config_path}")
    raw = config_path.read_bytes()
    if len(raw) > MAX_CONFIG_BYTES:
        raise RestoreError(f"local Git config exceeds quota: {config_path}")
    if raw.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")) or b"\x00" in raw:
        raise RestoreError(f"BOM/NUL local Git config is forbidden: {config_path}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RestoreError(f"local Git config is not strict UTF-8: {config_path}") from exc
    if any(line.rstrip().endswith("\\") for line in text.splitlines()):
        raise RestoreError(f"continued local Git config is forbidden: {config_path}")
    lowered = text.casefold()
    dangerous = (
        "[include]",
        "[includeif ",
        "[filter ",
        "[remote ",
        "[url ",
        "[credential",
        "[http",
        "[alias",
        "[submodule ",
        "worktree",
        "hookspath",
        "fsmonitor",
        "partialclone",
        "promisor",
        "alternate",
        "sshcommand",
    )
    hit = next((needle for needle in dangerous if needle in lowered), None)
    if hit is not None:
        raise RestoreError(f"dangerous local Git config token {hit!r}: {config_path}")
    return text


def validate_extracted_git_dir(git_dir: Path) -> None:
    reject_reparse_ancestors(git_dir)
    forbidden_paths = (
        git_dir / "commondir",
        git_dir / "config.worktree",
        git_dir / "worktrees",
        git_dir / "modules",
        git_dir / "objects" / "info" / "alternates",
        git_dir / "objects" / "info" / "http-alternates",
    )
    for path in forbidden_paths:
        if path.exists() or path.is_symlink():
            raise RestoreError(f"external/shared Git metadata is forbidden: {path}")
    for path in git_dir.rglob("*"):
        if _is_reparse_or_link(path):
            raise RestoreError(f"Git metadata reparse/link is forbidden: {path}")
        if path.name.endswith(".promisor"):
            raise RestoreError(f"lazy/promisor Git metadata is forbidden: {path}")
        if path.is_file() and not stat.S_ISREG(path.stat(follow_symlinks=False).st_mode):
            raise RestoreError(f"special Git metadata file is forbidden: {path}")
    _read_config_fail_closed(git_dir / "config")
    hooks = git_dir / "hooks"
    if hooks.exists():
        active_hooks = [
            path
            for path in hooks.rglob("*")
            if path.is_file() and not path.name.endswith(".sample")
        ]
        if active_hooks:
            raise RestoreError(f"active Git hooks are forbidden: {active_hooks[:5]}")


def harden_extracted_git_dir(git_dir: Path, *, object_format: str) -> None:
    validate_extracted_git_dir(git_dir)
    hooks = git_dir / "hooks"
    if hooks.exists():
        shutil.rmtree(hooks)
    hooks.mkdir(exist_ok=True)
    if object_format not in {"sha1", "sha256"}:
        raise RestoreError(f"unsupported Git object format: {object_format}")
    version = "1" if object_format == "sha256" else "0"
    extension = "\n[extensions]\n\tobjectFormat = sha256\n" if object_format == "sha256" else ""
    safe_config = (
        "[core]\n"
        f"\trepositoryFormatVersion = {version}\n"
        "\tfileMode = true\n"
        "\tbare = false\n"
        "\tlogAllRefUpdates = true\n"
        "\tlongPaths = true\n"
        f"{extension}"
    )
    temporary = git_dir / f"config.safe-{uuid.uuid4().hex}.tmp"
    temporary.write_text(safe_config, encoding="utf-8", newline="\n")
    os.replace(temporary, git_dir / "config")


def _exact_ref_map(git_dir: Path) -> dict[str, dict[str, str]]:
    _, all_output, _ = run_git(git_dir, "for-each-ref", "--format=%(refname)", "refs", git_dir=True)
    all_refs = sorted(line for line in all_output.splitlines() if line)
    unsupported = [name for name in all_refs if not name.startswith(("refs/heads/", "refs/tags/"))]
    if unsupported:
        raise RestoreError(f"unsupported ref namespaces: {unsupported}")
    _, output, _ = run_git(
        git_dir, "show-ref", "--heads", "--tags", git_dir=True, allowed_return_codes=(0, 1)
    )
    result: dict[str, dict[str, str]] = {}
    for line in output.splitlines():
        oid, separator, name = line.partition(" ")
        oid = oid.lower()
        if not separator or not OID_RE.fullmatch(oid) or name in result:
            raise RestoreError(f"malformed or duplicate Git ref: {line}")
        if not name.startswith(("refs/heads/", "refs/tags/")):
            raise RestoreError(f"unsupported Git ref: {name}")
        _, type_output, _ = run_git(git_dir, "cat-file", "-t", oid, git_dir=True)
        object_type = type_output.strip()
        allowed = {"commit"} if name.startswith("refs/heads/") else {"commit", "tag"}
        if object_type not in allowed:
            raise RestoreError(f"invalid ref object type: {name}={object_type}")
        _, peeled_output, _ = run_git(git_dir, "rev-parse", f"{name}^{{}}", git_dir=True)
        peeled_oid = peeled_output.strip().lower()
        _, peeled_type_output, _ = run_git(git_dir, "cat-file", "-t", peeled_oid, git_dir=True)
        if not OID_RE.fullmatch(peeled_oid) or peeled_type_output.strip() != "commit":
            raise RestoreError(f"ref does not peel to a commit: {name}")
        result[name] = {
            "oid": oid,
            "object_type": object_type,
            "peeled_oid": peeled_oid,
            "peeled_type": "commit",
        }
    if set(result) != set(all_refs):
        raise RestoreError("show-ref and complete refs inventory differ")
    return dict(sorted(result.items()))


def _expected_ref_map(record: dict[str, Any]) -> dict[str, dict[str, str]]:
    refs = record.get("refs")
    types = record.get("ref_types")
    details = record.get("ref_details")
    if not all(isinstance(value, dict) for value in (refs, types, details)):
        raise RestoreError(f"{record.get('id')} lacks the strict ref contract")
    if set(refs) != set(types) or set(refs) != set(details):
        raise RestoreError(f"{record.get('id')} ref contract key sets differ")
    result: dict[str, dict[str, str]] = {}
    for name, raw_oid in refs.items():
        oid = str(raw_oid).lower()
        object_type = str(types[name])
        detail = details[name]
        if not isinstance(detail, dict):
            raise RestoreError(f"invalid ref detail: {name}")
        value = {
            "oid": oid,
            "object_type": object_type,
            "peeled_oid": str(detail.get("peeled_oid", "")).lower(),
            "peeled_type": str(detail.get("peeled_type", "")),
        }
        if (
            not isinstance(name, str)
            or not name.startswith(("refs/heads/", "refs/tags/"))
            or not OID_RE.fullmatch(oid)
            or str(detail.get("oid", "")).lower() != oid
            or str(detail.get("object_type", "")) != object_type
            or not OID_RE.fullmatch(value["peeled_oid"])
            or value["peeled_type"] != "commit"
        ):
            raise RestoreError(f"invalid indexed ref detail: {name}")
        result[name] = value
    return dict(sorted(result.items()))


def _zero_unreachable(git_dir: Path) -> None:
    run_git(git_dir, "fsck", "--full", git_dir=True)
    _, output, error = run_git(
        git_dir, "fsck", "--full", "--unreachable", "--no-reflogs", git_dir=True
    )
    findings = [
        line
        for line in (*output.splitlines(), *error.splitlines())
        if re.match(r"^(?:unreachable|dangling)\s", line.strip(), re.IGNORECASE)
    ]
    if findings:
        raise RestoreError(f"strict zero-unreachable gate failed: {findings[:10]}")


def verify_git_metadata(record: dict[str, Any], git_dir: Path) -> dict[str, Any]:
    expected = _expected_ref_map(record)
    actual = _exact_ref_map(git_dir)
    if actual != expected:
        raise RestoreError(f"{record['id']} exact refs/type/peel map differs from index")
    _, head_output, _ = run_git(git_dir, "rev-parse", "HEAD", git_dir=True)
    head = head_output.strip().lower()
    _, symbolic_output, _ = run_git(git_dir, "symbolic-ref", "-q", "HEAD", git_dir=True)
    symbolic = symbolic_output.strip()
    _, format_output, _ = run_git(git_dir, "rev-parse", "--show-object-format", git_dir=True)
    object_format = format_output.strip()
    default_ref = f"refs/heads/{record['default_branch']}"
    if (
        head != str(record["head"]).lower()
        or symbolic != record.get("symbolic_head")
        or symbolic != default_ref
        or default_ref not in actual
        or actual[default_ref]["oid"] != head
        or object_format != record.get("object_format")
    ):
        raise RestoreError(f"{record['id']} HEAD/symbolic/default/object-format mismatch")
    _, shallow_output, _ = run_git(git_dir, "rev-parse", "--is-shallow-repository", git_dir=True)
    shallow = shallow_output.strip() == "true"
    shallow_file = git_dir / "shallow"
    boundaries = []
    if shallow_file.is_file():
        boundaries = sorted(
            {line.strip().lower() for line in shallow_file.read_text(encoding="ascii").splitlines() if line.strip()}
        )
    if any(not OID_RE.fullmatch(oid) for oid in boundaries):
        raise RestoreError(f"{record['id']} malformed shallow boundary")
    if shallow != bool(record.get("shallow")) or boundaries != sorted(record.get("shallow_boundary_oids", [])):
        raise RestoreError(f"{record['id']} shallow state mismatch")
    _zero_unreachable(git_dir)
    return {"head": head, "ref_count": len(actual), "shallow": shallow}


def _parse_sha256sums(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            raise RestoreError(f"malformed SHA256SUMS line {number}")
        digest, raw_path = match.groups()
        normalized, _, key = canonical_relative(raw_path, "SHA256SUMS path")
        if key in {item.casefold() for item in values}:
            raise RestoreError(f"duplicate/colliding SHA256SUMS path: {raw_path}")
        values[normalized] = digest
    return values


def _load_verifier(root: Path):
    verifier_path = Path(__file__).resolve().with_name("verify_private_transport_v3.py")
    if not verifier_path.is_file():
        # The distributed restore is placed at the wrapper root.
        verifier_path = root / "verify_private_transport_v3.py"
    if not verifier_path.is_file():
        raise RestoreError(f"strict archive-index verifier is missing: {verifier_path}")
    spec = importlib.util.spec_from_file_location("cockpit_transport_strict_verifier", verifier_path)
    if spec is None or spec.loader is None:
        raise RestoreError(f"cannot load strict archive-index verifier: {verifier_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_transport_before_selection(
    root: Path,
    *,
    expected_count: int,
    verifier_work_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    root = root.resolve()
    index_path = root / ".cockpit-transport" / "transport-index.json"
    sums_path = root / ".cockpit-transport" / "SHA256SUMS"
    manifest_path = root / "manifest.json"
    index = load_json_object(index_path)
    manifest = load_json_object(manifest_path)
    if index.get("schema_version") != TRANSPORT_SCHEMA:
        raise RestoreError(f"unsupported transport schema: {index.get('schema_version')}")
    records = index.get("repositories")
    manifest_records = manifest.get("repositories")
    if not isinstance(records, list) or not isinstance(manifest_records, list):
        raise RestoreError("transport and manifest repositories must be arrays")
    if index.get("repository_count") != expected_count or len(records) != expected_count:
        raise RestoreError("transport repository cardinality mismatch")
    if len(manifest_records) != expected_count:
        raise RestoreError("manifest repository cardinality mismatch")
    if sha256_file(manifest_path) != index.get("manifest_sha256"):
        raise RestoreError("manifest/index SHA-256 mismatch")
    sums = _parse_sha256sums(sums_path)
    manifest_by_id: dict[str, dict[str, Any]] = {}
    for entry in manifest_records:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise RestoreError("manifest repository entry is invalid")
        if entry["id"] in manifest_by_id:
            raise RestoreError(f"duplicate manifest id: {entry['id']}")
        manifest_by_id[entry["id"]] = entry
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    seen_archives: set[str] = set()
    expected_archive_paths: set[Path] = set()
    total_bytes = 0
    shallow_count = 0
    for record in records:
        if not isinstance(record, dict):
            raise RestoreError("transport repository entry is invalid")
        repo_id = record.get("id")
        if not isinstance(repo_id, str) or repo_id in seen_ids:
            raise RestoreError(f"duplicate/invalid transport id: {repo_id}")
        seen_ids.add(repo_id)
        relative, _, relative_key = canonical_relative(record.get("relative_path"), f"{repo_id} relative_path")
        archive_name, archive_parts, archive_key = canonical_relative(record.get("archive"), f"{repo_id} archive")
        if relative_key in seen_paths or archive_key in seen_archives:
            raise RestoreError(f"duplicate/canonical-colliding repository/archive path: {repo_id}")
        seen_paths.add(relative_key)
        seen_archives.add(archive_key)
        if not archive_name.startswith(".cockpit-transport/repositories/") or not archive_name.endswith(".git.tar"):
            raise RestoreError(f"archive path is outside the canonical repository inventory: {archive_name}")
        entry = manifest_by_id.get(repo_id)
        if entry is None:
            raise RestoreError(f"transport id is absent from manifest: {repo_id}")
        for index_field, manifest_field in (
            ("name", "name"),
            ("kind", "kind"),
            ("relative_path", "relative_path"),
            ("default_branch", "default_branch"),
            ("head", "repo_head"),
            ("branches", "branches"),
            ("tags", "tags"),
            ("git_tracked_files", "tracked_files"),
        ):
            if record.get(index_field) != entry.get(manifest_field):
                raise RestoreError(f"{repo_id} manifest/index field mismatch: {index_field}")
        archive_path = contained_target(root, archive_parts, f"{repo_id} archive")
        expected_archive_paths.add(archive_path.resolve())
        expected_digest = record.get("archive_sha256")
        expected_bytes = record.get("archive_bytes")
        if not isinstance(expected_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
            raise RestoreError(f"{repo_id} archive hash is invalid")
        if not isinstance(expected_bytes, int) or expected_bytes < 1:
            raise RestoreError(f"{repo_id} archive byte count is invalid")
        if sums.get(archive_name) != expected_digest:
            raise RestoreError(f"{repo_id} SHA256SUMS/index mismatch")
        inspect_archive(
            archive_path,
            expected_sha256=expected_digest,
            expected_bytes=expected_bytes,
        )
        _expected_ref_map(record)
        total_bytes += expected_bytes
        shallow_count += bool(record.get("shallow"))
    if set(manifest_by_id) != seen_ids:
        raise RestoreError("manifest and transport id sets differ")
    if set(sums) != {str(record["archive"]) for record in records}:
        raise RestoreError("SHA256SUMS inventory differs from transport index")
    if index.get("total_archive_bytes") not in (None, total_bytes):
        raise RestoreError("derived total_archive_bytes mismatch")
    if index.get("shallow_repository_count") not in (None, shallow_count):
        raise RestoreError("derived shallow_repository_count mismatch")
    archive_root = root / ".cockpit-transport" / "repositories"
    actual_entries: set[Path] = set()
    for item in archive_root.rglob("*"):
        if _is_reparse_or_link(item):
            raise RestoreError(f"transport inventory contains a reparse/link: {item}")
        if item.is_file():
            actual_entries.add(item.resolve())
        elif not item.is_dir():
            raise RestoreError(f"transport inventory contains a special entry: {item}")
    if actual_entries != expected_archive_paths:
        raise RestoreError("exact repository archive inventory mismatch")
    temporary = [item for item in (root / ".cockpit-transport").rglob("*") if item.name.endswith(".tmp")]
    if temporary:
        raise RestoreError(f"transport contains temporary artifacts: {temporary[:5]}")

    # Reuse the independent strict verifier, but replace its extractor with this
    # module's safe manual extractor before it sees any archive contents.
    verifier = _load_verifier(root)
    verifier.tempfile = types.SimpleNamespace(TemporaryDirectory=normal_temporary_directory)

    def verifier_safe_extract(
        path: Path,
        destination: Path,
        *,
        expected_size: int | None = None,
        expected_sha256: str | None = None,
        **future_options: Any,
    ) -> Path:
        matching = next((item for item in records if (root / item["archive"]).resolve() == path.resolve()), None)
        if matching is None:
            raise RestoreError(f"verifier requested an unknown archive: {path}")
        if expected_size not in (None, matching["archive_bytes"]):
            raise RestoreError(f"verifier archive-size contract drift: {path}")
        if expected_sha256 not in (None, matching["archive_sha256"]):
            raise RestoreError(f"verifier archive-hash contract drift: {path}")
        if future_options:
            raise RestoreError(
                f"unsupported future verifier extraction contract: {sorted(future_options)}"
            )
        git_dir = extract_archive_safely(
            path,
            destination,
            expected_sha256=matching["archive_sha256"],
            expected_bytes=matching["archive_bytes"],
        )
        # Preserve the archived bytes for the verifier's config/reflog/index
        # binding.  Manual validation has already rejected every executable or
        # host-dependent indirection; the real restore path below subsequently
        # replaces the config before its first repository Git operation.
        validate_extracted_git_dir(git_dir)
        return git_dir

    verifier.extract_archive = verifier_safe_extract
    result = verifier.verify(
        root,
        mode="archive-index",
        restored_root=None,
        expected_count=expected_count,
        work_root=verifier_work_root,
        allow_missing_ref_types=False,
    )
    if not result.get("valid"):
        raise RestoreError(f"strict archive-index verification failed: {result.get('issues')}")
    return index, manifest, records


def _verify_materialized_repository(record: dict[str, Any], repository: Path) -> dict[str, Any]:
    git_dir = repository / ".git"
    state = verify_git_metadata(record, git_dir)
    _, branch_output, _ = run_git(repository, "branch", "--format=%(refname:short)")
    _, tag_output, _ = run_git(repository, "tag", "--list")
    if sorted(branch_output.splitlines()) != sorted(record["branches"]):
        raise RestoreError(f"{record['id']} restored branches mismatch")
    if sorted(tag_output.splitlines()) != sorted(record["tags"]):
        raise RestoreError(f"{record['id']} restored tags mismatch")
    _, tracked_output, _ = run_git(repository, "ls-files", "-z")
    tracked_count = len([item for item in tracked_output.split("\x00") if item])
    if tracked_count != record["git_tracked_files"]:
        raise RestoreError(f"{record['id']} restored tracked-file count mismatch")
    _, remote_output, _ = run_git(repository, "remote")
    if remote_output.splitlines():
        raise RestoreError(f"{record['id']} restored repository has a remote")
    _, status_output, _ = run_git(repository, "status", "--porcelain=v1", "-z")
    if status_output:
        raise RestoreError(f"{record['id']} restored repository is dirty")
    _zero_unreachable(git_dir)
    return {**state, "branch_count": len(record["branches"]), "tag_count": len(record["tags"]), "git_tracked_files": tracked_count}


def restore(
    root: Path,
    destination_root: Path,
    *,
    repository_ids: list[str] | None = None,
    report_path: Path | None = None,
    expected_count: int = 40,
) -> dict[str, Any]:
    root = root.resolve()
    destination_root = destination_root.resolve(strict=False)
    reject_reparse_ancestors(root)
    # Verification must not write into the wrapper (the PowerShell default
    # destination) or into a not-yet-authorized destination.  Use a system-temp
    # sibling with a normal Windows ACL; only a passing strict archive-index
    # audit permits destination creation below.
    verifier_parent = Path(tempfile.gettempdir()).resolve()
    reject_reparse_ancestors(verifier_parent)
    try:
        verifier_parent.relative_to(root)
    except ValueError:
        pass
    else:
        raise RestoreError("system verifier scratch directory must be outside the wrapper")
    with normal_temporary_directory(prefix="cbv-", dir=verifier_parent) as verifier_work:
        index, _manifest, records = validate_transport_before_selection(
            root,
            expected_count=expected_count,
            verifier_work_root=Path(verifier_work),
        )
    reject_reparse_ancestors(
        destination_root.parent if not destination_root.exists() else destination_root
    )
    destination_root.mkdir(parents=True, exist_ok=True)
    by_id = {record["id"]: record for record in records}
    requested = list(dict.fromkeys(repository_ids or list(by_id)))
    unknown = sorted(set(requested) - set(by_id))
    if unknown:
        raise RestoreError(f"unknown repository ids: {unknown}")
    selected = [by_id[repo_id] for repo_id in requested]
    results: list[dict[str, Any]] = []
    staging_root = destination_root / f".cr-{uuid.uuid4().hex[:10]}"
    staging_root.mkdir(exist_ok=False)
    try:
        for record in selected:
            _, relative_parts, _ = canonical_relative(record["relative_path"], f"{record['id']} destination")
            target = contained_target(destination_root, relative_parts, f"{record['id']} destination")
            if target.exists():
                if not (target / ".git").is_dir() or _is_reparse_or_link(target):
                    raise RestoreError(f"refusing to overwrite existing non-repository path: {target}")
                # Existing repositories are not trusted merely because they
                # were restored once.  Reject every local redirection or
                # executable metadata mechanism before the first Git command.
                validate_extracted_git_dir(target / ".git")
                result = _verify_materialized_repository(record, target)
                results.append({"id": record["id"], "destination": str(target), "disposition": "verified_existing", **result})
                continue
            stage = staging_root / record["id"]
            _, archive_parts, _ = canonical_relative(record["archive"], f"{record['id']} archive")
            archive_path = contained_target(root, archive_parts, f"{record['id']} archive")
            git_dir = extract_archive_safely(
                archive_path,
                stage,
                expected_sha256=record["archive_sha256"],
                expected_bytes=record["archive_bytes"],
            )
            harden_extracted_git_dir(git_dir, object_format=record["object_format"])
            verify_git_metadata(record, git_dir)
            # Checkout the already verified full default ref, never a short branch name.
            default_ref = f"refs/heads/{record['default_branch']}"
            run_git(stage, "reset", "--hard", default_ref)
            result = _verify_materialized_repository(record, stage)
            target.parent.mkdir(parents=True, exist_ok=True)
            reject_reparse_ancestors(target.parent)
            os.replace(stage, target)
            results.append({"id": record["id"], "destination": str(target), "disposition": "restored", **result})
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
    output = {
        "schema_version": "1.0.0",
        "document_type": "cockpit_benchmark_safe_python_restore",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "valid": True,
        "transport_schema_version": index["schema_version"],
        "transport_index_sha256": sha256_file(root / ".cockpit-transport" / "transport-index.json"),
        "validated_repository_count": len(records),
        "selected_repository_count": len(selected),
        "restored_repository_count": sum(item["disposition"] == "restored" for item in results),
        "verified_existing_repository_count": sum(item["disposition"] == "verified_existing" for item in results),
        "destination_root": str(destination_root),
        "repositories": results,
    }
    rendered = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if report_path is not None:
        report = report_path.resolve(strict=False)
        report.parent.mkdir(parents=True, exist_ok=True)
        temporary = report.with_name(report.name + f".{uuid.uuid4().hex}.tmp")
        temporary.write_text(rendered, encoding="utf-8", newline="\n")
        os.replace(temporary, report)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--repository-id", action="append", dest="repository_ids")
    parser.add_argument("--report-path", type=Path)
    arguments = parser.parse_args()
    try:
        result = restore(
            arguments.root,
            arguments.destination_root,
            repository_ids=arguments.repository_ids,
            report_path=arguments.report_path,
            expected_count=40,
        )
    except (RestoreError, OSError, tarfile.TarError) as exc:
        print(f"restore failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
