# claude.ai / Claude Desktop'a yüklenecek .skill paketlerini (her skill için bir tane) dist\ altına üretir.
# Compress-Archive yerine ZipArchive kullanılır: zip içindeki yollar '/' ile yazılmalı,
# aksi hâlde paket macOS'ta ve claude.ai'de bozuk açılır.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$RepoDir   = Split-Path -Parent $PSScriptRoot
$Version   = (Get-Content (Join-Path $RepoDir '.claude-plugin\plugin.json') -Raw -Encoding UTF8 | ConvertFrom-Json).version
$SkillsDir = Join-Path $RepoDir 'skills'
$DistDir   = Join-Path $RepoDir 'dist'
$Skip      = @('.DS_Store', 'Thumbs.db', 'desktop.ini')

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

Get-ChildItem -Path $SkillsDir -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } | ForEach-Object {
    $name = $_.Name
    $out  = Join-Path $DistDir "$name-v$Version.skill"
    if (Test-Path $out) { Remove-Item $out }
    $zip = [IO.Compression.ZipFile]::Open($out, [IO.Compression.ZipArchiveMode]::Create)
    try {
        Get-ChildItem -Path $_.FullName -Recurse -File |
            Where-Object { $_.Name -notin $Skip -and $_.Extension -ne '.pyc' -and $_.FullName -notmatch '[\\/]__pycache__[\\/]' } |
            ForEach-Object {
                $rel = $_.FullName.Substring($SkillsDir.Length + 1) -replace '\\', '/'
                [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $rel) | Out-Null
            }
    } finally {
        $zip.Dispose()
    }
    Write-Host $out
}
