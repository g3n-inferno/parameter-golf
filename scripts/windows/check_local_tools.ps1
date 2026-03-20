# Intent: verify the local Windows environment needed for a smooth Runpod + Windsurf + Codex workflow.

[CmdletBinding()]
param(
    [string]$SshKeyPath = $env:RUNPOD_SSH_KEY_PATH
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-CommandAvailable {
    param([Parameter(Mandatory = $true)][string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-FirstExistingPath {
    param([Parameter(Mandatory = $true)][string[]]$Candidates)
    foreach ($candidate in $Candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
    }
    return $null
}

function Write-Status {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][bool]$Ok,
        [Parameter(Mandatory = $true)][string]$Detail
    )

    $prefix = if ($Ok) { "[ok]" } else { "[warn]" }
    Write-Host "$prefix $Label - $Detail"
}

function Get-SshKeyCandidates {
    param([string]$PreferredPath)

    $candidates = @()
    if ($PreferredPath) {
        $candidates += $PreferredPath
    }

    $userHome = [Environment]::GetFolderPath("UserProfile")
    $candidates += @(
        (Join-Path $userHome ".ssh\id_ed25519"),
        (Join-Path $userHome ".ssh\id_rsa"),
        (Join-Path $userHome ".ssh\id_ecdsa")
    )

    return $candidates | Select-Object -Unique
}

$requiredMissing = $false

$gitOk = Test-CommandAvailable -Name "git"
Write-Status -Label "git" -Ok $gitOk -Detail ($(if ($gitOk) { "available" } else { "missing" }))
if (-not $gitOk) { $requiredMissing = $true }

$sshOk = Test-CommandAvailable -Name "ssh"
Write-Status -Label "ssh" -Ok $sshOk -Detail ($(if ($sshOk) { "available" } else { "missing" }))
if (-not $sshOk) { $requiredMissing = $true }

$runpodctlOk = Test-CommandAvailable -Name "runpodctl"
$runpodctlKnownPath = Get-FirstExistingPath -Candidates @(
    (Join-Path $env:LOCALAPPDATA "runpodctl\runpodctl.exe"),
    (Join-Path $env:TEMP "runpodctl-install\runpodctl.exe")
)
$runpodctlDetail = if ($runpodctlOk) {
    "available on PATH"
} elseif ($runpodctlKnownPath) {
    "found outside PATH at $runpodctlKnownPath; open a new shell or update PATH"
} else {
    "optional, not found"
}
Write-Status -Label "runpodctl" -Ok ($runpodctlOk -or ($null -ne $runpodctlKnownPath)) -Detail $runpodctlDetail

$flashOk = Test-CommandAvailable -Name "flash"
$flashKnownPath = Get-FirstExistingPath -Candidates (
    @(Get-ChildItem -Path (Join-Path $env:APPDATA "Python") -Directory -ErrorAction SilentlyContinue |
        ForEach-Object { Join-Path $_.FullName "Scripts\flash.exe" })
)
$flashDetail = if ($flashOk) {
    "available on PATH"
} elseif ($flashKnownPath) {
    "found outside PATH at $flashKnownPath; open a new shell or update PATH"
} else {
    "optional, not found"
}
Write-Status -Label "flash" -Ok ($flashOk -or ($null -ne $flashKnownPath)) -Detail $flashDetail

$wslCmdOk = Test-CommandAvailable -Name "wsl"
if ($wslCmdOk) {
    $wslList = (& wsl -l -q 2>&1 | Out-String).Trim()
    $wslHasDistro = -not [string]::IsNullOrWhiteSpace($wslList) -and ($wslList -notmatch "no installed distributions")
    $wslDetail = if ($wslHasDistro) { "available with installed distro(s)" } else { "optional, command exists but no distro is installed" }
    Write-Status -Label "wsl" -Ok $wslHasDistro -Detail $wslDetail
} else {
    Write-Status -Label "wsl" -Ok $false -Detail "optional, not found"
}

$sshConfigPath = Join-Path ([Environment]::GetFolderPath("UserProfile")) ".ssh\config"
$sshConfigOk = Test-Path -LiteralPath $sshConfigPath
Write-Status -Label "ssh config" -Ok $sshConfigOk -Detail ($(if ($sshConfigOk) { $sshConfigPath } else { "optional, not found yet" }))

$existingKeys = @(Get-SshKeyCandidates -PreferredPath $SshKeyPath | Where-Object { Test-Path -LiteralPath $_ })
$keyOk = $existingKeys.Count -gt 0
if ($keyOk) {
    Write-Status -Label "ssh key" -Ok $true -Detail ($existingKeys[0])
} else {
    Write-Status -Label "ssh key" -Ok $false -Detail "set RUNPOD_SSH_KEY_PATH or place a key under ~/.ssh"
    $requiredMissing = $true
}

$authHintPaths = @(
    (Join-Path ([Environment]::GetFolderPath("UserProfile")) ".runpod\config.toml"),
    (Join-Path ([Environment]::GetFolderPath("UserProfile")) ".runpod\config.yaml"),
    (Join-Path $env:APPDATA "runpod\config.toml")
) | Where-Object { $_ }

$authHintFound = $false
if ($env:RUNPOD_API_KEY) {
    $authHintFound = $true
}
if ($authHintPaths | Where-Object { Test-Path -LiteralPath $_ }) {
    $authHintFound = $true
}

if ($runpodctlOk -or $runpodctlKnownPath) {
    $authMessage = if ($authHintFound) {
        "auth hint detected; still verify against current runpodctl prompts"
    } else {
        "no auth hint detected; runpodctl may still require login"
    }
    Write-Status -Label "runpodctl auth" -Ok $authHintFound -Detail $authMessage
}

Write-Host ""
Write-Host "Recommended next step:"
Write-Host "  ssh <your-runpod-host-alias>"
Write-Host "  then clone your fork into /workspace/parameter-golf if needed"
Write-Host "  then run bash scripts/runpod/bootstrap_pod.sh from the repo root"

if ($requiredMissing) {
    exit 1
}
