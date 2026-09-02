[CmdletBinding()]
param(
    [string] $DestinationRoot,
    [string[]] $RepositoryId,
    [string] $ReportPath,
    [string] $PythonExecutable
)

$ErrorActionPreference = 'Stop'
$DestinationRoot = if ($DestinationRoot) { $DestinationRoot } else { $PSScriptRoot }
$restoreScript = Join-Path $PSScriptRoot 'Restore-CockpitBenchmark.py'
if (-not (Test-Path -LiteralPath $restoreScript -PathType Leaf)) {
    throw "Safe Python restore tool is missing: $restoreScript"
}

$pythonPrefix = @()
if ($PythonExecutable) {
    $pythonCommand = $PythonExecutable
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCommand = (Get-Command py -ErrorAction Stop).Source
    $pythonPrefix = @('-3')
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCommand = (Get-Command python -ErrorAction Stop).Source
} else {
    throw 'Python 3 is required for the safe cockpit benchmark restore.'
}

$arguments = @(
    $restoreScript,
    '--root', $PSScriptRoot,
    '--destination-root', ([System.IO.Path]::GetFullPath($DestinationRoot))
)
if ($RepositoryId) {
    foreach ($id in $RepositoryId) {
        if ([string]::IsNullOrWhiteSpace($id)) {
            throw 'RepositoryId entries must not be empty.'
        }
        $arguments += @('--repository-id', $id)
    }
}
if ($ReportPath) {
    $arguments += @('--report-path', ([System.IO.Path]::GetFullPath($ReportPath)))
}

& $pythonCommand @pythonPrefix @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Safe Python restore failed with exit code $LASTEXITCODE."
}
