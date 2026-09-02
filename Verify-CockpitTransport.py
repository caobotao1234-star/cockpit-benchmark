#!/usr/bin/env python3
"""Verify cockpit transport refs and bytes without trusting the restore script.

The verifier has three deliberately separate modes:

``archive-index``
    Prove only that the transport index, archive bytes and SHA256SUMS agree.
    This mode does not claim that the transport represents the current source.
``source-index-archive``
    Additionally bind the current manifest and all live child repositories.
``full``
    Additionally bind a separately restored 40-repository tree.

Each ref comparison uses the complete ``refs/heads`` + ``refs/tags`` name/OID
map.  v0.3 indexes also carry the parallel ``ref_types`` map.  A legacy index
without ``ref_types`` is accepted only when the caller explicitly opts into
``--allow-missing-ref-types``; that exception is intended solely for auditing
the immutable v0.2 archive/index pair and cannot prove the v0.3 contract.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable


MODES = ("archive-index", "source-index-archive", "full")
OID_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
REF_PREFIXES = ("refs/heads/", "refs/tags/")
ALLOWED_TRANSPORT_SCHEMA = "2.0.0"
EXPECTED_DOCUMENT_TYPE = "cockpit_benchmark_private_transport"
EXPECTED_PACKAGING = "one path-safe complete .git metadata archive per independent child repository"
MAX_ARCHIVE_BYTES = 100_000_000
MAX_ARCHIVE_MEMBERS = 250_000
MAX_ARCHIVE_EXPANDED_BYTES = 100_000_000
WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}
BINDING_FIELDS = (
    "object_count",
    "object_inventory_sha256",
    "reflog_file_count",
    "reflog_inventory_sha256",
    "config_sha256",
    "index_entry_count",
    "index_inventory_sha256",
    "git_tracked_files",
    "payload_gitlink_count",
)


class VerificationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise VerificationError(f"expected a JSON object: {path}")
    return value


def safe_git_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for name in list(environment):
        if name.upper().startswith("GIT_"):
            environment.pop(name, None)
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
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_PROTOCOL_FROM_USER": "0",
            "GCM_INTERACTIVE": "Never",
        }
    )
    return environment


def run_git(
    location: Path,
    *arguments: str,
    git_dir: bool = False,
    allowed_return_codes: Iterable[int] = (0,),
) -> tuple[int, str, str]:
    prefix = [
        "git",
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
        "filter.lfs.required=false",
        "-c",
        "filter.lfs.smudge=",
        "-c",
        "filter.lfs.process=",
        "-c",
        "protocol.ext.allow=never",
    ]
    prefix.extend(["--git-dir", str(location)] if git_dir else ["-C", str(location)])
    completed = subprocess.run(
        [*prefix, *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=safe_git_environment(),
    )
    if completed.returncode not in set(allowed_return_codes):
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise VerificationError(
            f"git {' '.join(arguments)} failed in {location} "
            f"({completed.returncode}): {detail}"
        )
    return completed.returncode, completed.stdout, completed.stderr


def add_issue(
    issues: list[dict[str, Any]],
    code: str,
    detail: str,
    *,
    repo_id: str | None = None,
    leg: str | None = None,
) -> None:
    value: dict[str, Any] = {"code": code, "detail": detail}
    if repo_id is not None:
        value["repo_id"] = repo_id
    if leg is not None:
        value["leg"] = leg
    issues.append(value)


def normalized_index_refs(
    record: dict[str, Any],
    issues: list[dict[str, Any]],
    *,
    require_types: bool,
    allow_missing_types: bool,
) -> tuple[dict[str, str], dict[str, str], dict[str, dict[str, str]]]:
    repo_id = str(record.get("id", "<missing>"))
    refs_value = record.get("refs")
    if not isinstance(refs_value, dict):
        add_issue(issues, "index_refs_missing", "refs must be an object", repo_id=repo_id)
        return {}, {}, {}
    refs: dict[str, str] = {}
    for name, oid_value in refs_value.items():
        if not isinstance(name, str) or not name.startswith(REF_PREFIXES):
            add_issue(issues, "index_ref_name_invalid", str(name), repo_id=repo_id)
            continue
        oid = str(oid_value).lower()
        if not OID_RE.fullmatch(oid):
            add_issue(issues, "index_ref_oid_invalid", f"{name}={oid_value}", repo_id=repo_id)
            continue
        refs[name] = oid

    types_value = record.get("ref_types")
    if types_value is None:
        if require_types and not allow_missing_types:
            add_issue(
                issues,
                "index_ref_types_missing",
                "v0.3 requires ref_types for every indexed ref",
                repo_id=repo_id,
            )
        return refs, {}, {}
    if not isinstance(types_value, dict):
        add_issue(issues, "index_ref_types_invalid", "ref_types must be an object", repo_id=repo_id)
        return refs, {}, {}
    types = {str(name): str(value) for name, value in types_value.items()}
    if set(types) != set(refs):
        add_issue(
            issues,
            "index_ref_type_keys_mismatch",
            f"refs-only={sorted(set(refs) - set(types))}, "
            f"types-only={sorted(set(types) - set(refs))}",
            repo_id=repo_id,
        )
    for name, object_type in sorted(types.items()):
        allowed = {"commit"} if name.startswith("refs/heads/") else {"commit", "tag"}
        if object_type not in allowed:
            add_issue(
                issues,
                "index_ref_type_invalid",
                f"{name}={object_type}; allowed={sorted(allowed)}",
                repo_id=repo_id,
            )
    details_value = record.get("ref_details")
    details: dict[str, dict[str, str]] = {}
    if details_value is None:
        if require_types and not allow_missing_types:
            add_issue(
                issues,
                "index_ref_details_missing",
                "v0.3 requires direct and peeled facts for every indexed ref",
                repo_id=repo_id,
            )
        return refs, types, details
    if not isinstance(details_value, dict) or set(details_value) != set(refs):
        add_issue(
            issues,
            "index_ref_details_invalid",
            "ref_details must be an object with exactly the refs keys",
            repo_id=repo_id,
        )
        return refs, types, details
    for name, raw in details_value.items():
        if not isinstance(raw, dict):
            add_issue(issues, "index_ref_detail_invalid", name, repo_id=repo_id)
            continue
        detail = {key: str(raw.get(key, "")) for key in ("oid", "object_type", "peeled_oid", "peeled_type")}
        if (
            detail["oid"] != refs.get(name)
            or detail["object_type"] != types.get(name)
            or not OID_RE.fullmatch(detail["peeled_oid"])
            or detail["peeled_type"] != "commit"
        ):
            add_issue(
                issues,
                "index_ref_detail_mismatch",
                f"{name}: {detail}",
                repo_id=repo_id,
            )
        details[name] = detail
    return refs, types, details


def exact_ref_map(location: Path, *, git_dir: bool) -> dict[str, dict[str, str]]:
    _, all_ref_output, _ = run_git(
        location,
        "for-each-ref",
        "--format=%(refname)",
        "refs",
        git_dir=git_dir,
    )
    unsupported = sorted(
        name
        for name in all_ref_output.splitlines()
        if name and not name.startswith(REF_PREFIXES)
    )
    if unsupported:
        raise VerificationError(f"unsupported ref namespaces in {location}: {unsupported}")
    _, output, _ = run_git(
        location,
        "show-ref",
        "--heads",
        "--tags",
        git_dir=git_dir,
        allowed_return_codes=(0, 1),
    )
    result: dict[str, dict[str, str]] = {}
    for line in output.splitlines():
        oid, separator, name = line.partition(" ")
        oid = oid.lower()
        if not separator or not OID_RE.fullmatch(oid) or not name.startswith(REF_PREFIXES):
            raise VerificationError(f"malformed show-ref record in {location}: {line}")
        if name in result:
            raise VerificationError(f"duplicate ref in {location}: {name}")
        _, type_output, _ = run_git(location, "cat-file", "-t", oid, git_dir=git_dir)
        object_type = type_output.strip()
        allowed = {"commit"} if name.startswith("refs/heads/") else {"commit", "tag"}
        if object_type not in allowed:
            raise VerificationError(
                f"unsupported ref type in {location}: {name} -> {oid} ({object_type})"
            )
        _, peeled_output, _ = run_git(location, "rev-parse", f"{name}^{{}}", git_dir=git_dir)
        peeled_oid = peeled_output.strip().lower()
        _, peeled_type_output, _ = run_git(
            location, "cat-file", "-t", peeled_oid, git_dir=git_dir
        )
        peeled_type = peeled_type_output.strip()
        if not OID_RE.fullmatch(peeled_oid) or peeled_type != "commit":
            raise VerificationError(
                f"ref does not peel to a commit in {location}: "
                f"{name} -> {peeled_oid} ({peeled_type})"
            )
        result[name] = {
            "oid": oid,
            "object_type": object_type,
            "peeled_oid": peeled_oid,
            "peeled_type": peeled_type,
        }
    return dict(sorted(result.items()))


def compare_ref_map(
    expected_oids: dict[str, str],
    expected_types: dict[str, str],
    expected_details: dict[str, dict[str, str]],
    actual: dict[str, dict[str, str]],
    issues: list[dict[str, Any]],
    *,
    repo_id: str,
    leg: str,
) -> None:
    actual_names = set(actual)
    expected_names = set(expected_oids)
    missing = sorted(expected_names - actual_names)
    extra = sorted(actual_names - expected_names)
    if missing:
        add_issue(issues, "ref_missing", str(missing), repo_id=repo_id, leg=leg)
    if extra:
        add_issue(issues, "ref_extra", str(extra), repo_id=repo_id, leg=leg)
    for name in sorted(expected_names & actual_names):
        if actual[name]["oid"] != expected_oids[name]:
            add_issue(
                issues,
                "ref_oid_mismatch",
                f"{name}: {actual[name]['oid']} != {expected_oids[name]}",
                repo_id=repo_id,
                leg=leg,
            )
        if name in expected_types and actual[name]["object_type"] != expected_types[name]:
            add_issue(
                issues,
                "ref_type_mismatch",
                f"{name}: {actual[name]['object_type']} != {expected_types[name]}",
                repo_id=repo_id,
                leg=leg,
            )
        if name in expected_details:
            for field in ("peeled_oid", "peeled_type"):
                if actual[name][field] != expected_details[name][field]:
                    add_issue(
                        issues,
                        f"ref_{field}_mismatch",
                        f"{name}: {actual[name][field]} != {expected_details[name][field]}",
                        repo_id=repo_id,
                        leg=leg,
                    )


def ref_map_sha256(value: dict[str, dict[str, str]]) -> str:
    rendered = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def repository_state(location: Path, *, git_dir: bool) -> dict[str, Any]:
    _, head_output, _ = run_git(location, "rev-parse", "HEAD", git_dir=git_dir)
    symbolic_code, symbolic_output, _ = run_git(
        location,
        "symbolic-ref",
        "-q",
        "HEAD",
        git_dir=git_dir,
        allowed_return_codes=(0, 1),
    )
    _, format_output, _ = run_git(
        location, "rev-parse", "--show-object-format", git_dir=git_dir
    )
    _, shallow_output, _ = run_git(
        location, "rev-parse", "--is-shallow-repository", git_dir=git_dir
    )
    if git_dir:
        shallow_path = location / "shallow"
    else:
        _, shallow_path_output, _ = run_git(
            location, "rev-parse", "--git-path", "shallow", git_dir=False
        )
        raw_path = Path(shallow_path_output.strip())
        shallow_path = raw_path if raw_path.is_absolute() else (location / raw_path)
    boundaries: list[str] = []
    if shallow_path.is_file():
        raw_boundaries = [
            line.strip().lower()
            for line in shallow_path.read_text(encoding="ascii").splitlines()
            if line.strip()
        ]
        boundaries = sorted(set(raw_boundaries))
    if any(not OID_RE.fullmatch(oid) for oid in boundaries):
        raise VerificationError(f"invalid shallow boundary in {location}: {boundaries}")
    shallow = shallow_output.strip() == "true"
    if shallow != bool(boundaries):
        raise VerificationError(
            f"shallow flag/boundary mismatch in {location}: shallow={shallow}, "
            f"boundaries={boundaries}"
        )
    return {
        "head": head_output.strip().lower(),
        "symbolic_head": symbolic_output.strip() if symbolic_code == 0 else None,
        "object_format": format_output.strip(),
        "shallow": shallow,
        "shallow_boundary_oids": boundaries,
    }


def tree_inventory(root: Path) -> tuple[int, str]:
    if not root.exists():
        return 0, hashlib.sha256(b"").hexdigest()
    records: list[bytes] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold()):
        relative = path.relative_to(root).as_posix()
        metadata = path.lstat()
        if path.is_symlink() or not (stat.S_ISDIR(metadata.st_mode) or stat.S_ISREG(metadata.st_mode)):
            raise VerificationError(f"unsupported metadata filesystem entry: {path}")
        if stat.S_ISREG(metadata.st_mode):
            payload = path.read_bytes()
            records.append(
                relative.encode("utf-8")
                + b"\x00"
                + str(len(payload)).encode("ascii")
                + b"\x00"
                + hashlib.sha256(payload).hexdigest().encode("ascii")
                + b"\n"
            )
    rendered = b"".join(records)
    return len(records), hashlib.sha256(rendered).hexdigest()


def git_directory_for(location: Path, *, git_dir: bool) -> Path:
    if git_dir:
        value = location.resolve()
    else:
        _, output, _ = run_git(location, "rev-parse", "--absolute-git-dir")
        value = Path(output.strip()).resolve()
        expected = (location / ".git").resolve()
        if value != expected or not expected.is_dir():
            raise VerificationError(f"worktree does not use an internal .git directory: {location}")
        try:
            value.relative_to(location.resolve())
        except ValueError as exc:
            raise VerificationError(f".git directory escapes worktree: {location}") from exc
    return value


def safe_config_sha256(location: Path, git_directory: Path, *, git_dir: bool) -> str:
    if (git_directory / "commondir").exists():
        raise VerificationError(f"external Git common directory is forbidden: {git_directory}")
    alternates = git_directory / "objects" / "info" / "alternates"
    if alternates.exists() and alternates.read_text(encoding="utf-8").strip():
        raise VerificationError(f"external Git object alternates are forbidden: {git_directory}")
    _, key_output, _ = run_git(
        location,
        "config",
        "--local",
        "--name-only",
        "--get-regexp",
        ".*",
        git_dir=git_dir,
        allowed_return_codes=(0, 1),
    )
    for key in key_output.splitlines():
        lowered = key.casefold()
        if (
            lowered in {
                "core.hookspath",
                "core.fsmonitor",
                "core.worktree",
                "core.attributesfile",
                "extensions.worktreeconfig",
            }
            or lowered.startswith(("include.", "includeif.", "filter.", "remote.", "submodule."))
        ):
            raise VerificationError(f"unsafe or host-dependent Git config key: {key}")
    _, remote_output, _ = run_git(location, "remote", git_dir=git_dir)
    if remote_output.splitlines():
        raise VerificationError(f"repository unexpectedly has remotes: {remote_output.strip()}")
    config = git_directory / "config"
    if not config.is_file():
        raise VerificationError(f"Git config is missing: {config}")
    return hashlib.sha256(config.read_bytes()).hexdigest()


def repository_binding(location: Path, *, git_dir: bool) -> dict[str, Any]:
    git_directory = git_directory_for(location, git_dir=git_dir)
    config_sha = safe_config_sha256(location, git_directory, git_dir=git_dir)
    _, object_output, _ = run_git(
        location,
        "cat-file",
        "--batch-all-objects",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        git_dir=git_dir,
    )
    object_lines = sorted(line for line in object_output.splitlines() if line)
    object_rendered = "\n".join(object_lines).encode("utf-8") + (b"\n" if object_lines else b"")
    _, index_output, _ = run_git(location, "ls-files", "--stage", "-z", git_dir=git_dir)
    _, tracked_output, _ = run_git(location, "ls-files", "-z", git_dir=git_dir)
    _, payload_output, _ = run_git(location, "ls-tree", "-r", "-z", "HEAD", git_dir=git_dir)
    payload_gitlinks = [
        record
        for record in payload_output.split("\x00")
        if record and record.split(" ", 1)[0] == "160000"
    ]
    _, fsck_output, fsck_error = run_git(
        location, "fsck", "--full", "--unreachable", git_dir=git_dir
    )
    unreachable = [
        line
        for line in (fsck_output + "\n" + fsck_error).splitlines()
        if line.startswith(("unreachable ", "dangling "))
    ]
    if unreachable:
        raise VerificationError(f"repository contains unreachable objects: {unreachable[:5]}")
    reflog_count, reflog_sha = tree_inventory(git_directory / "logs")
    return {
        "object_count": len(object_lines),
        "object_inventory_sha256": hashlib.sha256(object_rendered).hexdigest(),
        "reflog_file_count": reflog_count,
        "reflog_inventory_sha256": reflog_sha,
        "config_sha256": config_sha,
        "index_entry_count": len([item for item in index_output.split("\x00") if item]),
        "index_inventory_sha256": hashlib.sha256(index_output.encode("utf-8")).hexdigest(),
        "git_tracked_files": len([item for item in tracked_output.split("\x00") if item]),
        "payload_gitlink_count": len(payload_gitlinks),
        "payload_gitlinks": payload_gitlinks,
    }


def compare_repository_binding(
    record: dict[str, Any],
    binding: dict[str, Any],
    issues: list[dict[str, Any]],
    *,
    repo_id: str,
    leg: str,
    allow_missing_metadata: bool,
    compare_mutable_metadata: bool,
) -> None:
    required = set(BINDING_FIELDS)
    if not compare_mutable_metadata:
        required -= {"config_sha256", "reflog_file_count", "reflog_inventory_sha256"}
    for field in sorted(required):
        expected = record.get(field)
        if expected is None:
            if not allow_missing_metadata:
                add_issue(
                    issues,
                    "index_binding_metadata_missing",
                    field,
                    repo_id=repo_id,
                    leg=leg,
                )
        elif binding[field] != expected:
            add_issue(
                issues,
                f"{field}_mismatch",
                f"{binding[field]} != {expected}",
                repo_id=repo_id,
                leg=leg,
            )
    if binding["payload_gitlink_count"]:
        add_issue(
            issues,
            "payload_gitlink",
            str(binding["payload_gitlinks"]),
            repo_id=repo_id,
            leg=leg,
        )


def compare_repository_state(
    record: dict[str, Any],
    state: dict[str, Any],
    ref_map: dict[str, dict[str, str]],
    issues: list[dict[str, Any]],
    *,
    repo_id: str,
    leg: str,
    allow_missing_metadata: bool,
) -> None:
    expected_symbolic = record.get("symbolic_head")
    expected_object_format = record.get("object_format")
    expected_boundaries = record.get("shallow_boundary_oids")
    missing = [
        name
        for name, value in (
            ("symbolic_head", expected_symbolic),
            ("object_format", expected_object_format),
            ("shallow_boundary_oids", expected_boundaries),
        )
        if value is None
    ]
    if missing and not allow_missing_metadata:
        add_issue(
            issues,
            "index_state_metadata_missing",
            str(missing),
            repo_id=repo_id,
            leg=leg,
        )
    expected_default_symbolic = f"refs/heads/{record.get('default_branch')}"
    if state["symbolic_head"] != expected_default_symbolic:
        add_issue(
            issues,
            "symbolic_head_mismatch",
            f"{state['symbolic_head']} != {expected_default_symbolic}",
            repo_id=repo_id,
            leg=leg,
        )
    default_fact = ref_map.get(expected_default_symbolic)
    if default_fact is None or default_fact["oid"] != state["head"]:
        add_issue(
            issues,
            "default_branch_head_mismatch",
            f"HEAD={state['head']}, default_ref={default_fact}",
            repo_id=repo_id,
            leg=leg,
        )
    for field, expected in (
        ("head", record.get("head")),
        ("symbolic_head", expected_symbolic),
        ("object_format", expected_object_format),
        ("shallow", record.get("shallow")),
        ("shallow_boundary_oids", expected_boundaries),
    ):
        if expected is not None and state[field] != expected:
            add_issue(
                issues,
                f"{field}_mismatch",
                f"{state[field]} != {expected}",
                repo_id=repo_id,
                leg=leg,
            )


def safe_relative(root: Path, value: str, label: str) -> Path:
    candidate = (root / Path(*PurePosixPath(value).parts)).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise VerificationError(f"{label} escapes root: {value}") from exc
    return candidate


def archive_member_parts(name: str) -> tuple[str, ...]:
    if not name or "\\" in name or "\x00" in name:
        raise VerificationError(f"non-portable archive member name: {name!r}")
    raw_parts = name.split("/")
    pure = PurePosixPath(name)
    windows = PureWindowsPath(name)
    if (
        pure.is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or any(part in {"", ".", ".."} for part in raw_parts)
        or tuple(raw_parts) != pure.parts
        or not raw_parts
        or raw_parts[0] != ".git"
    ):
        raise VerificationError(f"unsafe archive member name: {name!r}")
    for part in raw_parts:
        if (
            ":" in part
            or part.endswith((" ", "."))
            or any(ord(character) < 32 for character in part)
            or part.split(".", 1)[0].casefold() in WINDOWS_RESERVED_NAMES
        ):
            raise VerificationError(f"Windows-unsafe archive member name: {name!r}")
    return tuple(raw_parts)


def validated_archive_members(
    archive: tarfile.TarFile, label: str
) -> list[tuple[tarfile.TarInfo, tuple[str, ...]]]:
    members = archive.getmembers()
    if not members:
        raise VerificationError(f"empty archive: {label}")
    if len(members) > MAX_ARCHIVE_MEMBERS:
        raise VerificationError(
            f"archive member quota exceeded in {label}: {len(members)} > {MAX_ARCHIVE_MEMBERS}"
        )
    expanded = 0
    names: set[tuple[str, ...]] = set()
    result: list[tuple[tarfile.TarInfo, tuple[str, ...]]] = []
    for member in members:
        parts = archive_member_parts(member.name)
        canonical = tuple(part.casefold() for part in parts)
        if canonical in names:
            raise VerificationError(
                f"duplicate or Windows-aliased archive member in {label}: {member.name}"
            )
        names.add(canonical)
        if member.issym() or member.islnk() or not (member.isdir() or member.isfile()):
            raise VerificationError(f"unsupported archive member in {label}: {member.name}")
        if member.size < 0 or member.size > MAX_ARCHIVE_EXPANDED_BYTES:
            raise VerificationError(f"archive member size quota exceeded: {member.name}")
        if member.isfile():
            expanded += member.size
            if expanded > MAX_ARCHIVE_EXPANDED_BYTES:
                raise VerificationError(
                    f"archive expanded-size quota exceeded in {label}: "
                    f"{expanded} > {MAX_ARCHIVE_EXPANDED_BYTES}"
                )
        result.append((member, parts))
    return result


def read_archive_payload(
    path: Path, *, expected_size: int | None = None, expected_sha256: str | None = None
) -> tuple[bytes, str]:
    size = path.stat().st_size
    if size <= 0 or size > MAX_ARCHIVE_BYTES:
        raise VerificationError(f"archive byte quota violated for {path}: {size}")
    if expected_size is not None and size != expected_size:
        raise VerificationError(f"archive size mismatch for {path}: {size} != {expected_size}")
    payload = path.read_bytes()
    if len(payload) != size:
        raise VerificationError(f"archive size changed while reading: {path}")
    digest = hashlib.sha256(payload).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise VerificationError(
            f"archive SHA-256 mismatch for {path}: {digest} != {expected_sha256}"
        )
    return payload, digest


def validate_archive_members(path: Path) -> list[tarfile.TarInfo]:
    payload, _ = read_archive_payload(path)
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as archive:
        return [member for member, _ in validated_archive_members(archive, str(path))]


def extract_archive(
    path: Path,
    destination: Path,
    *,
    expected_size: int | None = None,
    expected_sha256: str | None = None,
) -> Path:
    payload, _ = read_archive_payload(
        path, expected_size=expected_size, expected_sha256=expected_sha256
    )
    destination.mkdir(parents=True, exist_ok=False)
    destination_root = destination.resolve()
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as archive:
        for member, parts in validated_archive_members(archive, str(path)):
            target = destination.joinpath(*parts).resolve(strict=False)
            try:
                target.relative_to(destination_root)
            except ValueError as exc:
                raise VerificationError(
                    f"archive member escapes extraction root: {member.name}"
                ) from exc
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise VerificationError(f"cannot read archive member: {member.name}")
            with source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
    git_dir = destination / ".git"
    if not git_dir.is_dir():
        raise VerificationError(f"archive did not produce .git: {path}")
    return git_dir


def outer_gitlink_paths(root: Path) -> list[str]:
    if not (root / ".git").exists():
        raise VerificationError(f"outer wrapper is not a Git repository: {root}")
    results: set[str] = set()
    for label, arguments in (
        ("index", ("ls-files", "--stage", "-z")),
        ("HEAD", ("ls-tree", "-r", "-z", "HEAD")),
    ):
        _, output, _ = run_git(root, *arguments)
        for record in output.split("\x00"):
            if not record:
                continue
            metadata, separator, path = record.partition("\t")
            mode = metadata.split(" ", 1)[0]
            if not separator:
                raise VerificationError(f"malformed outer {label} record: {record}")
            if mode == "160000":
                results.add(f"{label}:{path}")
    return sorted(results)


def canonical_path_key(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def exact_filesystem_inventory(root: Path) -> tuple[list[Path], list[Path]]:
    if not root.is_dir():
        raise VerificationError(f"inventory root is missing: {root}")
    files: list[Path] = []
    directories: list[Path] = []

    def visit(directory: Path) -> None:
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                metadata = entry.stat(follow_symlinks=False)
                attributes = getattr(metadata, "st_file_attributes", 0)
                reparse = bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
                if entry.is_symlink() or reparse:
                    raise VerificationError(f"symlink/reparse point in transport inventory: {path}")
                if stat.S_ISDIR(metadata.st_mode):
                    directories.append(path.resolve())
                    visit(path)
                elif stat.S_ISREG(metadata.st_mode):
                    files.append(path.resolve())
                else:
                    raise VerificationError(f"special entry in transport inventory: {path}")

    visit(root)
    return sorted(files), sorted(directories)


def verify(
    root: Path,
    *,
    mode: str,
    restored_root: Path | None,
    expected_count: int,
    work_root: Path,
    allow_missing_ref_types: bool,
) -> dict[str, Any]:
    root = root.resolve()
    work_root = work_root.resolve()
    if mode not in MODES:
        raise VerificationError(f"unsupported mode: {mode}")
    if allow_missing_ref_types and mode != "archive-index":
        raise VerificationError(
            "--allow-missing-ref-types is restricted to legacy archive-index audits"
        )
    if mode == "full" and restored_root is None:
        raise VerificationError("full mode requires restored_root")
    if restored_root is not None:
        restored_root = restored_root.resolve()

    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    transport_root = root / ".cockpit-transport"
    index_path = transport_root / "transport-index.json"
    sums_path = transport_root / "SHA256SUMS"
    index = load_object(index_path)
    records_value = index.get("repositories")
    if index.get("schema_version") != ALLOWED_TRANSPORT_SCHEMA:
        add_issue(issues, "index_schema", str(index.get("schema_version")))
    if index.get("document_type") != EXPECTED_DOCUMENT_TYPE:
        add_issue(issues, "index_document_type", str(index.get("document_type")))
    if index.get("packaging") != EXPECTED_PACKAGING:
        add_issue(issues, "index_packaging", str(index.get("packaging")))
    if index.get("manifest") != "manifest.json":
        add_issue(issues, "index_manifest_path", str(index.get("manifest")))
    if not isinstance(records_value, list):
        raise VerificationError("transport index repositories must be an array")
    records = [item for item in records_value if isinstance(item, dict)]
    if len(records) != len(records_value):
        add_issue(issues, "index_record_type", "every repository record must be an object")
    if index.get("repository_count") != expected_count or len(records) != expected_count:
        add_issue(
            issues,
            "repository_count",
            f"index={index.get('repository_count')}, records={len(records)}, expected={expected_count}",
        )

    ids = [str(item.get("id")) for item in records]
    archives = [str(item.get("archive")) for item in records]
    relative_paths = [str(item.get("relative_path")) for item in records]
    for label, values in (("id", ids), ("archive", archives), ("relative_path", relative_paths)):
        normalized = [value.casefold() for value in values]
        duplicates = sorted(
            {values[index] for index, value in enumerate(normalized) if normalized.count(value) > 1}
        )
        if duplicates:
            add_issue(issues, f"duplicate_{label}", str(duplicates))

    expected_archive_paths: dict[str, Path] = {}
    seen_archive_targets: dict[str, str] = {}
    seen_repository_targets: dict[str, str] = {}
    for record in records:
        repo_id = str(record.get("id"))
        archive_value = str(record.get("archive"))
        try:
            archive_path = safe_relative(root, archive_value, f"archive {repo_id}")
        except VerificationError as exc:
            add_issue(issues, "archive_path", str(exc), repo_id=repo_id)
            continue
        repository_archive_root = (transport_root / "repositories").resolve()
        try:
            archive_path.relative_to(repository_archive_root)
        except ValueError:
            add_issue(
                issues,
                "archive_location",
                f"not below .cockpit-transport/repositories: {archive_value}",
                repo_id=repo_id,
            )
            continue
        if not archive_value.endswith(".git.tar"):
            add_issue(issues, "archive_suffix", archive_value, repo_id=repo_id)
        archive_key = canonical_path_key(archive_path)
        if archive_key in seen_archive_targets:
            add_issue(
                issues,
                "duplicate_archive_canonical",
                f"{archive_value} aliases {seen_archive_targets[archive_key]}",
                repo_id=repo_id,
            )
        else:
            seen_archive_targets[archive_key] = archive_value
        expected_archive_paths[repo_id] = archive_path
        try:
            repository_path = safe_relative(
                root, str(record.get("relative_path")), f"repository {repo_id}"
            )
            repository_key = canonical_path_key(repository_path)
            if repository_key in seen_repository_targets:
                add_issue(
                    issues,
                    "duplicate_relative_path_canonical",
                    f"{record.get('relative_path')} aliases "
                    f"{seen_repository_targets[repository_key]}",
                    repo_id=repo_id,
                )
            else:
                seen_repository_targets[repository_key] = str(record.get("relative_path"))
        except VerificationError as exc:
            add_issue(issues, "relative_path", str(exc), repo_id=repo_id)

    repository_archive_root = transport_root / "repositories"
    try:
        inventory_files, inventory_directories = exact_filesystem_inventory(transport_root)
    except (OSError, VerificationError) as exc:
        add_issue(issues, "transport_inventory", str(exc))
        inventory_files, inventory_directories = [], []
    actual_files = sorted(
        path for path in inventory_files if canonical_path_key(path).startswith(
            canonical_path_key(repository_archive_root) + os.sep
        )
    )
    expected_files = sorted({path for path in expected_archive_paths.values()})
    missing_files = [str(path.relative_to(root)) for path in expected_files if not path.is_file()]
    extra_files = [str(path.relative_to(root)) for path in actual_files if path not in expected_files]
    if missing_files:
        add_issue(issues, "archive_missing", str(missing_files))
    if extra_files:
        add_issue(issues, "archive_extra", str(extra_files))
    expected_transport_files = {
        index_path.resolve(),
        sums_path.resolve(),
        *expected_files,
    }
    unexpected_transport_files = sorted(
        str(path.relative_to(root)) for path in inventory_files if path not in expected_transport_files
    )
    expected_directories = {repository_archive_root.resolve()}
    for path in expected_files:
        parent = path.parent.resolve()
        while parent != transport_root.resolve():
            expected_directories.add(parent)
            parent = parent.parent
    unexpected_directories = sorted(
        str(path.relative_to(root))
        for path in inventory_directories
        if path not in expected_directories
    )
    if unexpected_transport_files or unexpected_directories:
        add_issue(
            issues,
            "transport_inventory_extra",
            f"files={unexpected_transport_files}, directories={unexpected_directories}",
        )
    temporary_files = sorted(
        str(path.relative_to(root))
        for path in transport_root.rglob("*")
        if path.is_file() and path.name.endswith(".tmp")
    )
    if temporary_files:
        add_issue(issues, "transport_tmp", str(temporary_files))

    try:
        gitlinks = outer_gitlink_paths(root)
    except VerificationError as exc:
        add_issue(issues, "outer_git", str(exc))
        gitlinks = []
    if gitlinks:
        add_issue(issues, "outer_gitlink", str(gitlinks))
    try:
        _, outer_status, _ = run_git(root, "status", "--porcelain=v1", "-z")
        if outer_status:
            add_issue(issues, "outer_dirty", "outer wrapper worktree/index is not clean")
    except VerificationError as exc:
        add_issue(issues, "outer_git", str(exc))

    expected_sums_lines: list[str] = []
    archive_bytes_total = 0
    largest_archive = 0
    for record in records:
        repo_id = str(record.get("id"))
        archive_path = expected_archive_paths.get(repo_id)
        if archive_path is None or not archive_path.is_file():
            continue
        try:
            _, digest = read_archive_payload(archive_path)
            size = archive_path.stat().st_size
        except (OSError, VerificationError) as exc:
            add_issue(issues, "archive_read", str(exc), repo_id=repo_id)
            continue
        archive_bytes_total += size
        largest_archive = max(largest_archive, size)
        if size != record.get("archive_bytes"):
            add_issue(
                issues,
                "archive_size_mismatch",
                f"{size} != {record.get('archive_bytes')}",
                repo_id=repo_id,
            )
        if digest != record.get("archive_sha256"):
            add_issue(
                issues,
                "archive_sha256_mismatch",
                f"{digest} != {record.get('archive_sha256')}",
                repo_id=repo_id,
            )
        expected_sums_lines.append(f"{record.get('archive_sha256')}  {record.get('archive')}\n")
    if index.get("total_archive_bytes") != archive_bytes_total:
        add_issue(
            issues,
            "total_archive_bytes_mismatch",
            f"{index.get('total_archive_bytes')} != {archive_bytes_total}",
        )
    indexed_shallow_count = sum(record.get("shallow") is True for record in records)
    if index.get("shallow_repository_count") != indexed_shallow_count:
        add_issue(
            issues,
            "shallow_repository_count_mismatch",
            f"{index.get('shallow_repository_count')} != {indexed_shallow_count}",
        )
    expected_sums = "".join(expected_sums_lines).encode("utf-8")
    actual_sums = sums_path.read_bytes() if sums_path.is_file() else b""
    normalized_sums = actual_sums.replace(b"\r\n", b"\n")
    if b"\r" in normalized_sums or normalized_sums != expected_sums:
        add_issue(issues, "sha256sums_mismatch", "SHA256SUMS differs from ordered index records")

    manifest: dict[str, Any] | None = None
    manifest_by_id: dict[str, dict[str, Any]] = {}
    if mode in {"source-index-archive", "full"}:
        manifest_path = root / "manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        manifest_records = manifest.get("repositories") if isinstance(manifest, dict) else None
        if not isinstance(manifest_records, list):
            raise VerificationError("manifest repositories must be an array")
        manifest_by_id = {
            str(item.get("id")): item for item in manifest_records if isinstance(item, dict)
        }
        if len(manifest_by_id) != len(manifest_records):
            add_issue(issues, "manifest_duplicate_or_invalid_records", "manifest ids are not unique")
        current_manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        if current_manifest_sha != index.get("manifest_sha256"):
            add_issue(
                issues,
                "manifest_sha256_mismatch",
                f"{current_manifest_sha} != {index.get('manifest_sha256')}",
                leg="source",
            )
        if set(manifest_by_id) != set(ids):
            add_issue(
                issues,
                "manifest_id_set_mismatch",
                f"manifest-only={sorted(set(manifest_by_id)-set(ids))}, "
                f"index-only={sorted(set(ids)-set(manifest_by_id))}",
                leg="source",
            )

    work_root.mkdir(parents=True, exist_ok=True)
    repository_results: list[dict[str, Any]] = []
    for record in records:
        repo_id = str(record.get("id"))
        record_start = len(issues)
        expected_refs, expected_types, expected_details = normalized_index_refs(
            record,
            issues,
            require_types=True,
            allow_missing_types=allow_missing_ref_types,
        )
        legacy_metadata_missing = any(
            record.get(name) is None
            for name in (
                "ref_types",
                "ref_details",
                "symbolic_head",
                "object_format",
                "shallow_boundary_oids",
                *BINDING_FIELDS,
            )
        )
        if legacy_metadata_missing and allow_missing_ref_types:
            warnings.append(
                {
                    "code": "legacy_ref_metadata_missing",
                    "repo_id": repo_id,
                    "detail": "OID/archive self-consistency can be audited, but the full v0.3 ref/state contract is not present",
                }
            )
        derived_branches = sorted(
            name.removeprefix("refs/heads/")
            for name in expected_refs
            if name.startswith("refs/heads/")
        )
        derived_tags = sorted(
            name.removeprefix("refs/tags/")
            for name in expected_refs
            if name.startswith("refs/tags/")
        )
        if record.get("branches") != derived_branches:
            add_issue(issues, "derived_branches_mismatch", str(record.get("branches")), repo_id=repo_id)
        if record.get("tags") != derived_tags:
            add_issue(issues, "derived_tags_mismatch", str(record.get("tags")), repo_id=repo_id)

        leg_maps: dict[str, dict[str, dict[str, str]]] = {}
        leg_states: dict[str, dict[str, Any]] = {}
        archive_path = expected_archive_paths.get(repo_id)
        if archive_path is not None and archive_path.is_file():
            try:
                with tempfile.TemporaryDirectory(prefix=f"transport-{repo_id}-", dir=work_root) as temp:
                    extracted_git = extract_archive(
                        archive_path,
                        Path(temp) / "repo",
                        expected_size=record.get("archive_bytes"),
                        expected_sha256=record.get("archive_sha256"),
                    )
                    archive_map = exact_ref_map(extracted_git, git_dir=True)
                    leg_maps["archive"] = archive_map
                    archive_state = repository_state(extracted_git, git_dir=True)
                    leg_states["archive"] = archive_state
                    compare_ref_map(
                        expected_refs,
                        expected_types,
                        expected_details,
                        archive_map,
                        issues,
                        repo_id=repo_id,
                        leg="archive",
                    )
                    compare_repository_state(
                        record,
                        archive_state,
                        archive_map,
                        issues,
                        repo_id=repo_id,
                        leg="archive",
                        allow_missing_metadata=allow_missing_ref_types,
                    )
                    archive_binding = repository_binding(extracted_git, git_dir=True)
                    compare_repository_binding(
                        record,
                        archive_binding,
                        issues,
                        repo_id=repo_id,
                        leg="archive",
                        allow_missing_metadata=allow_missing_ref_types,
                        compare_mutable_metadata=True,
                    )
            except (OSError, tarfile.TarError, VerificationError) as exc:
                add_issue(issues, "archive_verification", str(exc), repo_id=repo_id, leg="archive")

        if mode in {"source-index-archive", "full"}:
            manifest_entry = manifest_by_id.get(repo_id)
            if manifest_entry is None:
                add_issue(issues, "manifest_entry_missing", repo_id, repo_id=repo_id, leg="source")
            else:
                for field in ("name", "kind", "relative_path", "default_branch"):
                    if manifest_entry.get(field) != record.get(field):
                        add_issue(
                            issues,
                            "manifest_index_field_mismatch",
                            f"{field}: {manifest_entry.get(field)} != {record.get(field)}",
                            repo_id=repo_id,
                            leg="source",
                        )
                try:
                    source_repo = safe_relative(root, str(record.get("relative_path")), f"source {repo_id}")
                    if not (source_repo / ".git").is_dir():
                        raise VerificationError("not an independent Git worktree")
                    source_map = exact_ref_map(source_repo, git_dir=False)
                    leg_maps["source"] = source_map
                    source_state = repository_state(source_repo, git_dir=False)
                    leg_states["source"] = source_state
                    compare_ref_map(
                        expected_refs,
                        expected_types,
                        expected_details,
                        source_map,
                        issues,
                        repo_id=repo_id,
                        leg="source",
                    )
                    compare_repository_state(
                        record,
                        source_state,
                        source_map,
                        issues,
                        repo_id=repo_id,
                        leg="source",
                        allow_missing_metadata=allow_missing_ref_types,
                    )
                    source_binding = repository_binding(source_repo, git_dir=False)
                    compare_repository_binding(
                        record,
                        source_binding,
                        issues,
                        repo_id=repo_id,
                        leg="source",
                        allow_missing_metadata=False,
                        compare_mutable_metadata=True,
                    )
                    source_head = source_state["head"]
                    if source_head != manifest_entry.get("repo_head"):
                        add_issue(
                            issues,
                            "manifest_head_mismatch",
                            f"{source_head} != {manifest_entry.get('repo_head')}",
                            repo_id=repo_id,
                            leg="source",
                        )
                    _, status, _ = run_git(source_repo, "status", "--porcelain=v1", "-z")
                    if status:
                        add_issue(issues, "worktree_dirty", "source worktree is dirty", repo_id=repo_id, leg="source")
                    _, remote_output, _ = run_git(source_repo, "remote")
                    if remote_output.splitlines():
                        add_issue(issues, "remote_present", remote_output.strip(), repo_id=repo_id, leg="source")
                    source_map_after = exact_ref_map(source_repo, git_dir=False)
                    source_state_after = repository_state(source_repo, git_dir=False)
                    source_binding_after = repository_binding(source_repo, git_dir=False)
                    if (
                        source_map_after != source_map
                        or source_state_after != source_state
                        or source_binding_after != source_binding
                    ):
                        add_issue(
                            issues,
                            "source_changed_during_verification",
                            "source refs/state/objects/metadata changed during verification",
                            repo_id=repo_id,
                            leg="source",
                        )
                except VerificationError as exc:
                    add_issue(issues, "source_verification", str(exc), repo_id=repo_id, leg="source")

        if mode == "full" and restored_root is not None:
            try:
                restored_repo = safe_relative(
                    restored_root,
                    str(record.get("relative_path")),
                    f"restored {repo_id}",
                )
                if not (restored_repo / ".git").is_dir():
                    raise VerificationError("not an independent restored Git worktree")
                restored_map = exact_ref_map(restored_repo, git_dir=False)
                leg_maps["restored"] = restored_map
                restored_state = repository_state(restored_repo, git_dir=False)
                leg_states["restored"] = restored_state
                compare_ref_map(
                    expected_refs,
                    expected_types,
                    expected_details,
                    restored_map,
                    issues,
                    repo_id=repo_id,
                    leg="restored",
                )
                compare_repository_state(
                    record,
                    restored_state,
                    restored_map,
                    issues,
                    repo_id=repo_id,
                    leg="restored",
                    allow_missing_metadata=allow_missing_ref_types,
                )
                restored_binding = repository_binding(restored_repo, git_dir=False)
                compare_repository_binding(
                    record,
                    restored_binding,
                    issues,
                    repo_id=repo_id,
                    leg="restored",
                    allow_missing_metadata=False,
                    compare_mutable_metadata=False,
                )
                _, status, _ = run_git(restored_repo, "status", "--porcelain=v1", "-z")
                if status:
                    add_issue(issues, "worktree_dirty", "restored worktree is dirty", repo_id=repo_id, leg="restored")
                _, remote_output, _ = run_git(restored_repo, "remote")
                if remote_output.splitlines():
                    add_issue(issues, "remote_present", remote_output.strip(), repo_id=repo_id, leg="restored")
            except VerificationError as exc:
                add_issue(issues, "restored_verification", str(exc), repo_id=repo_id, leg="restored")

        repository_results.append(
            {
                "id": repo_id,
                "valid": len(issues) == record_start,
                "expected_ref_count": len(expected_refs),
                "expected_refs_sha256": ref_map_sha256(
                    {
                        name: {
                            "oid": oid,
                            "object_type": expected_types.get(name, "<legacy-unbound>"),
                            "peeled_oid": expected_details.get(name, {}).get(
                                "peeled_oid", "<legacy-unbound>"
                            ),
                            "peeled_type": expected_details.get(name, {}).get(
                                "peeled_type", "<legacy-unbound>"
                            ),
                        }
                        for name, oid in sorted(expected_refs.items())
                    }
                ),
                "legs": {
                    name: {
                        "ref_count": len(ref_map),
                        "refs_sha256": ref_map_sha256(ref_map),
                        "refs": ref_map,
                        "state": leg_states.get(name),
                    }
                    for name, ref_map in sorted(leg_maps.items())
                },
            }
        )

    return {
        "schema_version": "1.0.0",
        "document_type": "cockpit_benchmark_transport_v3_verification",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": mode,
        "root": str(root),
        "restored_root": str(restored_root) if restored_root is not None else None,
        "transport_index_sha256": sha256(index_path),
        "sha256sums_sha256": sha256(sums_path) if sums_path.is_file() else None,
        "index_manifest_sha256": index.get("manifest_sha256"),
        "repository_count": len(records),
        "archive_count": len(actual_files),
        "archive_bytes": archive_bytes_total,
        "largest_archive_bytes": largest_archive,
        "outer_gitlink_count": len(gitlinks),
        "temporary_file_count": len(temporary_files),
        "legacy_ref_types_missing_count": sum(
            warning["code"] == "legacy_ref_metadata_missing" for warning in warnings
        ),
        "valid_repository_count": sum(item["valid"] for item in repository_results),
        "repositories": repository_results,
        "warnings": warnings,
        "issues": issues,
        "valid": not issues,
    }


def atomic_new_json(path: Path, value: Any) -> None:
    path = path.resolve()
    if path.exists():
        raise VerificationError(f"refusing to overwrite report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise VerificationError(f"unexpected report temporary exists: {temporary}")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--restored-root", type=Path)
    parser.add_argument("--expected-count", type=int, default=40)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--allow-missing-ref-types", action="store_true")
    args = parser.parse_args()
    try:
        result = verify(
            args.root,
            mode=args.mode,
            restored_root=args.restored_root,
            expected_count=args.expected_count,
            work_root=args.work_root,
            allow_missing_ref_types=args.allow_missing_ref_types,
        )
        atomic_new_json(args.report, result)
    except (OSError, ValueError, json.JSONDecodeError, VerificationError) as exc:
        print(f"transport verification error: {exc}")
        return 2
    print(
        json.dumps(
            {
                "valid": result["valid"],
                "mode": result["mode"],
                "repository_count": result["repository_count"],
                "archive_count": result["archive_count"],
                "valid_repository_count": result["valid_repository_count"],
                "legacy_ref_types_missing_count": result["legacy_ref_types_missing_count"],
                "issue_count": len(result["issues"]),
                "report": str(args.report.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
