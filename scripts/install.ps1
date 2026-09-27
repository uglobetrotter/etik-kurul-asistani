# Windows kurulumu: skills\ altındaki her skill'i %USERPROFILE%\.claude\skills altına
# bağlar ya da kopyalar.
#   .\scripts\install.ps1              dizin bağlantısı (junction; yönetici izni gerekmez, git pull ile güncellenir)
#   .\scripts\install.ps1 -Copy        bağımsız kopya
#   .\scripts\install.ps1 -Uninstall   bu repodan kurulan skill'leri kaldırır
[CmdletBinding()]
param(
    [switch]$Copy,
    [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'

$RepoDir    = Split-Path -Parent $PSScriptRoot
$SkillsRoot = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $env:USERPROFILE '.claude\skills' }

New-Item -ItemType Directory -Force -Path $SkillsRoot | Out-Null

Get-ChildItem -Path (Join-Path $RepoDir 'skills') -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
    ForEach-Object {
        $src  = $_.FullName
        $dest = Join-Path $SkillsRoot $_.Name
        if (Test-Path $dest) {
            $item = Get-Item $dest -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                # Yalnız bağlantıyı siler; hedef klasöre dokunmaz.
                cmd /c rmdir "$dest" | Out-Null
            } else {
                $backup = "$dest.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                Move-Item $dest $backup
                Write-Host "Var olan kurulum yedeklendi: $backup"
            }
        }
        if ($Uninstall) {
            Write-Host "Kaldırıldı: $dest"
        } elseif ($Copy) {
            Copy-Item -Recurse $src $dest
            Write-Host "Kopyalandı: $dest"
        } else {
            New-Item -ItemType Junction -Path $dest -Target $src | Out-Null
            Write-Host "Bağlandı:   $dest"
        }
    }


if (-not $Uninstall) { Write-Host "Claude Code'u yeniden başlatın; /skills listesinde görünmeliler." }
