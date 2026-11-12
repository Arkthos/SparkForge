<#
.SYNOPSIS
Parse explicitly selected, hash-verified PowerShell source without executing it.
.DESCRIPTION
Requires PowerShell 7. SourceRoot, Inventory and Output must all be explicit.
Only Output is written. No account, remote service, source script or profile is run.
.EXAMPLE
pwsh -NoProfile -File .\research_tools\repository_study\parse_powershell.ps1 -Help
#>
[CmdletBinding()]
param(
    [string]$SourceRoot,
    [string]$Inventory,
    [string]$Output,
    [switch]$Help
)
$ErrorActionPreference = 'Stop'
if ($Help) {
    Write-Output 'Required: -SourceRoot <snapshot directory> -Inventory <inventory.json> -Output <receipt.json>'
    exit 0
}
if (-not $SourceRoot -or -not $Inventory -or -not $Output) {
    Write-Error 'Explicit SourceRoot, Inventory and Output parameters are required.'
    exit 2
}
function Assert-Unlinked([string]$Path) {
    $item = [System.IO.DirectoryInfo]::new([System.IO.Path]::GetFullPath($Path))
    while ($null -ne $item) {
        if (Test-Path -LiteralPath $item.FullName) {
            $entry = Get-Item -LiteralPath $item.FullName -Force
            if ($entry.LinkType -in @('SymbolicLink', 'Junction')) {
                throw 'Linked paths are not supported.'
            }
        }
        $item = $item.Parent
    }
}
Assert-Unlinked $SourceRoot
Assert-Unlinked $Inventory
Assert-Unlinked $Output
$source = [System.IO.Path]::GetFullPath($SourceRoot).TrimEnd('\', '/')
if (-not (Test-Path -LiteralPath $source -PathType Container)) { throw 'Missing source root.' }
$destination = [System.IO.Path]::GetFullPath($Output)
if ($destination.StartsWith($source + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase) -or
    $destination -eq [System.IO.Path]::GetFullPath($Inventory)) {
    throw 'Output must not overwrite source files or the source inventory.'
}
$inventoryData = Get-Content -LiteralPath $Inventory -Raw | ConvertFrom-Json -AsHashtable
$files = @($inventoryData.entries | Where-Object {
    $_.git_type -eq 'blob' -and $_.extension -eq '.ps1' -and $_.materialization -eq 'exact_blob_bytes'
})
if ($files.Count -eq 0) { throw 'No ordinary PowerShell source files were selected.' }
$seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$results = @(
    foreach ($entry in $files) {
        if (-not $seen.Add($entry.path)) { throw 'Duplicate PowerShell source path.' }
        $parts = $entry.path.Split('/')
        foreach ($part in $parts) {
            if (-not $part -or $part -in @('.', '..') -or $part -match '[<>:"|?*\\]' -or $part.TrimEnd(' ', '.') -ne $part) {
                throw 'Unsafe source path.'
            }
        }
        $path = [System.IO.Path]::GetFullPath((Join-Path $source ($entry.path.Replace('/', '\'))))
        Assert-Unlinked $path
        if (-not $path.StartsWith($source + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw 'Source path leaves the selected root.'
        }
        if ((Get-Item -LiteralPath $path).Length -gt 67108864) { throw 'Source exceeds the byte bound.' }
        $data = [System.IO.File]::ReadAllBytes($path)
        $hash = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($data)).ToLowerInvariant()
        if ($data.Length -ne $entry.size_bytes -or $hash -ne $entry.sha256) { throw 'Source hash or size mismatch.' }
        $encoding = [System.Text.UTF8Encoding]::new($false, $true)
        $text = $encoding.GetString($data).TrimStart([char]0xFEFF)
        $tokens = $null
        $errors = $null
        [void][System.Management.Automation.Language.Parser]::ParseInput($text, [ref]$tokens, [ref]$errors)
        [ordered]@{
            path = $entry.path
            status = if ($errors.Count -eq 0) { 'PASS' } else { 'FAIL' }
            error_count = $errors.Count
            error_lines = @($errors | ForEach-Object { $_.Extent.StartLineNumber })
        }
    }
)
$parent = Split-Path -Parent $destination
if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw 'The explicit output parent must exist.' }
[ordered]@{
    scope = 'PowerShell parsing only; no source scripts executed'
    commit = $inventoryData.snapshot.commit
    powershell_version = $PSVersionTable.PSVersion.ToString()
    checks = $results
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $destination -Encoding utf8
$failures = @($results | Where-Object { $_.status -eq 'FAIL' })
Write-Output "Parsed $($results.Count) PowerShell files; $($failures.Count) parse failures."
if ($failures.Count) { exit 1 }
