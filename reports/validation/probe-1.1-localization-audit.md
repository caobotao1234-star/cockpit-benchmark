# Probe 1.1 Android Localization Exclusion Audit

Date: 2026-08-29  
Status: **APPLIED — FOUR G3 APP REPOSITORIES REPAIRED AND RE-ACCEPTED**

## Rule correction

`cockpit-repo-probe` 1.0.0 counted localized Android resources such as `res/values-fr`,
`values-en-rGB`, and `values-b+sr+Latn` as source files and logical LOC. That contradicted the
benchmark rule excluding translation resources from production size.

Version 1.1.0 excludes locale-qualified `values-*` directories but retains non-language device and
UI qualifiers such as `values-night`, `values-land`, and `values-h800dp`. A regression test covers
legacy, region, BCP-47, versioned locale, base, night, and dimension cases.

## Recomputed inventory

| ID | Old files/LOC | New files/LOC | Old band | New band | Action |
|---|---:|---:|---|---|---|
| APP-02 | 943 / 32,888 | 356 / 26,344 | medium | small | reopened |
| APP-16 | 959 / 33,323 | 372 / 26,862 | medium | small | reopened |
| APP-04 | 217 / 10,073 | 133 / 8,729 | small | below floor | reopened |
| APP-18 | 215 / 10,050 | 131 / 8,706 | small | below floor | reopened |

APP-03, APP-17, FW-02, FW-03, FW-04, FW-15, FW-17, and FW-18 have no localized-resource count
change and retain their accepted bands. Therefore G2 remains passed; only G3 production inventory
is reduced.

## State transition and validation

- The four affected APP entries were removed from active `manifest.json`; their repositories,
  oracle files, and historical reports remain available as repair inputs.
- Their `g3-matrix.json` status is `planned`. Launcher targets are revised to 350–450 files and
  30k–36k LOC; Media targets are revised to 150–190 files and 10k–13k LOC.
- Active manifest count changed from 12 to 8. The eight retained entries were regenerated with
  probe 1.1.0 facts and `manifest.md` was rerendered.
- G3 matrix validation passes with zero issues. The eight active repositories pass fresh
  `git clone --no-hardlinks`, manifest/oracle/HEAD/statistics/feature checks with zero issues.

Machine-readable details are in `probe-1.1-localization-audit.json` and individual v1.1 probes.
No repository was deleted and no remote operation was performed.

## Remediation result

The four repositories were subsequently repaired using only non-localized tracked code, tests,
build files, and public lineage:

| Family | High | Low | File ratio | LOC ratio |
|---|---:|---:|---:|---:|
| Media small | APP-04 174 / 10,037 | APP-18 180 / 10,016 | 1.034 | 1.002 |
| Launcher medium | APP-02 413 / 36,269 | APP-16 514 / 40,968 | 1.245 | 1.130 |

All four are restored to the probe-1.1 manifest and verified G3 matrix status. The active
12-repository benchmark passes fresh clone smoke and deterministic validation with zero issues.
Media added 58/42 compilable runtime class files and the high side passed 27/27 JVM tests;
Launcher used the locked public Car SystemUI boundary on the high side and real platform-stack
copies on the low side. No localized resource was reintroduced into size statistics.
