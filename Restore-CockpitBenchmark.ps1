[CmdletBinding()]
param(
    [string] $DestinationRoot = $PSScriptRoot,
    [string[]] $RepositoryId,
    [string] $ReportPath
)

$ErrorActionPreference = 'Stop'

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string] $Repository,
        [Parameter(Mandatory = $true)][string[]] $GitArguments
    )

    $output = & git -C $Repository @GitArguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArguments -join ' ') failed in ${Repository}: $($output -join [Environment]::NewLine)"
    }
    return @($output)
}

function Assert-EqualList {
    param(
        [string] $Label,
        [string[]] $Actual,
        [string[]] $Expected
    )

    $actualText = (@($Actual | Sort-Object) -join "`n")
    $expectedText = (@($Expected | Sort-Object) -join "`n")
    if ($actualText -cne $expectedText) {
        throw "${Label} mismatch. Actual=[$($Actual -join ', ')], expected=[$($Expected -join ', ')]"
    }
}

$transportRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$destination = [System.IO.Path]::GetFullPath($DestinationRoot)
$indexPath = Join-Path $transportRoot '.cockpit-transport\transport-index.json'
$manifestPath = Join-Path $transportRoot 'manifest.json'

if (-not (Test-Path -LiteralPath $indexPath -PathType Leaf)) {
    throw "Transport index is missing: $indexPath"
}
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Manifest is missing: $manifestPath"
}

$index = Get-Content -LiteralPath $indexPath -Raw | ConvertFrom-Json
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($index.schema_version -ne '2.0.0' -or $index.repository_count -ne 40) {
    throw 'Unsupported or incomplete transport index.'
}

$manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($manifestHash -cne $index.manifest_sha256) {
    throw "manifest.json SHA-256 mismatch: $manifestHash != $($index.manifest_sha256)"
}

$selected = @($index.repositories)
if ($RepositoryId) {
    $requested = @($RepositoryId | Sort-Object -Unique)
    $known = @($selected.id)
    $unknown = @($requested | Where-Object { $_ -notin $known })
    if ($unknown.Count -gt 0) {
        throw "Unknown repository id(s): $($unknown -join ', ')"
    }
    $selected = @($selected | Where-Object { $_.id -in $requested })
}

$destinationPrefix = $destination.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
$restored = 0
$verifiedExisting = 0
$repositoryResults = @()

foreach ($record in $selected) {
    $manifestEntry = @($manifest.repositories | Where-Object id -eq $record.id)
    if ($manifestEntry.Count -ne 1) {
        throw "Manifest entry is missing or duplicated for $($record.id)"
    }
    if ($manifestEntry[0].repo_head -cne $record.head) {
        throw "Manifest/index HEAD mismatch for $($record.id)"
    }

    $archive = [System.IO.Path]::GetFullPath((Join-Path $transportRoot $record.archive))
    $transportPrefix = $transportRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $archive.StartsWith($transportPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Repository archive path escapes transport root: $archive"
    }
    if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) {
        throw "Repository archive is missing: $archive"
    }
    $archiveHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($archiveHash -cne $record.archive_sha256) {
        throw "Repository archive SHA-256 mismatch for $($record.id)"
    }

    $target = [System.IO.Path]::GetFullPath((Join-Path $destination $record.relative_path))
    if (-not $target.StartsWith($destinationPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Repository path escapes destination root: $target"
    }

    $existingRepository = Test-Path -LiteralPath (Join-Path $target '.git') -PathType Container
    if (-not $existingRepository) {
        if (Test-Path -LiteralPath $target) {
            $existingItems = @(Get-ChildItem -LiteralPath $target -Force)
            if ($existingItems.Count -gt 0) {
                throw "Refusing to overwrite non-empty non-repository path: $target"
            }
        } else {
            New-Item -ItemType Directory -Path $target -Force | Out-Null
        }

        & tar -xf $archive -C $target 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Repository archive extraction failed for $($record.id)"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $target '.git') -PathType Container)) {
            throw "Repository archive did not create .git for $($record.id)"
        }
        Invoke-Git -Repository $target -GitArguments @(
            'config', '--local', 'core.longpaths', 'true'
        ) | Out-Null
        Invoke-Git -Repository $target -GitArguments @(
            'reset', '--hard', $record.default_branch
        ) | Out-Null
        $restored += 1
    } else {
        $verifiedExisting += 1
    }

    $actualHead = [string](
        Invoke-Git -Repository $target -GitArguments @('rev-parse', 'HEAD') |
            Select-Object -First 1
    )
    $actualHead = $actualHead.Trim()
    if ($actualHead -cne $record.head) {
        throw "Restored HEAD mismatch for $($record.id): $actualHead != $($record.head)"
    }
    $actualShallow = [string](
        Invoke-Git -Repository $target -GitArguments @('rev-parse', '--is-shallow-repository') |
            Select-Object -First 1
    )
    if (($actualShallow.Trim() -eq 'true') -ne [bool]$record.shallow) {
        throw "Shallow-boundary mismatch for $($record.id)"
    }
    $actualBranches = @(
        Invoke-Git -Repository $target -GitArguments @('branch', '--format=%(refname:short)') |
            Where-Object { $_ }
    )
    $actualTags = @(
        Invoke-Git -Repository $target -GitArguments @('tag', '--list') |
            Where-Object { $_ }
    )
    Assert-EqualList -Label "$($record.id) branches" -Actual $actualBranches -Expected @($record.branches)
    Assert-EqualList -Label "$($record.id) tags" -Actual $actualTags -Expected @($record.tags)

    $actualTracked = @(
        Invoke-Git -Repository $target -GitArguments @('ls-files') | Where-Object { $_ }
    ).Count
    if ($actualTracked -ne $record.git_tracked_files) {
        throw "Git tracked-file mismatch for $($record.id): $actualTracked != $($record.git_tracked_files)"
    }
    if (@(Invoke-Git -Repository $target -GitArguments @('remote') | Where-Object { $_ }).Count -ne 0) {
        throw "Restored repository unexpectedly has a remote: $($record.id)"
    }
    if (@(Invoke-Git -Repository $target -GitArguments @('status', '--porcelain') | Where-Object { $_ }).Count -ne 0) {
        throw "Restored repository is dirty: $($record.id)"
    }
    Invoke-Git -Repository $target -GitArguments @('fsck', '--full') | Out-Null
    $repositoryResults += [pscustomobject]@{
        id = $record.id
        destination = $target
        head = $actualHead
        shallow = [bool]$record.shallow
        branch_count = $actualBranches.Count
        tag_count = $actualTags.Count
        git_tracked_files = $actualTracked
        remote_count = 0
        clean = $true
        fsck = 'passed'
        disposition = if ($existingRepository) { 'verified_existing' } else { 'restored' }
    }
    Write-Host "Verified $($record.id) -> $target"
}

$result = [pscustomobject]@{
    schema_version = '1.0.0'
    document_type = 'cockpit_benchmark_private_transport_restore'
    generated_at = [DateTime]::UtcNow.ToString('o')
    valid = $true
    transport_schema_version = $index.schema_version
    transport_index_sha256 = (Get-FileHash -LiteralPath $indexPath -Algorithm SHA256).Hash.ToLowerInvariant()
    selected_repository_count = $selected.Count
    restored_repository_count = $restored
    verified_existing_repository_count = $verifiedExisting
    destination_root = $destination
    repositories = $repositoryResults
}

$rendered = $result | ConvertTo-Json -Depth 8
if ($ReportPath) {
    $resolvedReport = [System.IO.Path]::GetFullPath($ReportPath)
    $reportParent = [System.IO.Path]::GetDirectoryName($resolvedReport)
    New-Item -ItemType Directory -Path $reportParent -Force | Out-Null
    [System.IO.File]::WriteAllText($resolvedReport, $rendered + "`n", [System.Text.UTF8Encoding]::new($false))
}
$rendered
