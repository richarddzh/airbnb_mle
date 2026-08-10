param(
    [string]$RepoId = "richarddzh/tiny-qwen3-30m-zh-completion",
    [string]$Proxy = "http://127.0.0.1:10808",
    [string]$HfExecutable = ""
)

$ErrorActionPreference = "Stop"

if ($Proxy) {
    $env:HTTP_PROXY = $Proxy
    $env:HTTPS_PROXY = $Proxy
    Remove-Item Env:ALL_PROXY -ErrorAction SilentlyContinue
}

if (-not $HfExecutable) {
    $hfCommand = Get-Command hf -ErrorAction SilentlyContinue
    if ($hfCommand) {
        $HfExecutable = $hfCommand.Source
    }
}

if (-not $HfExecutable -and $env:VIRTUAL_ENV) {
    $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\hf.exe"
    if (Test-Path $candidate) {
        $HfExecutable = $candidate
    }
}

if (-not $HfExecutable) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $candidate = Join-Path (Split-Path $pythonCommand.Source) "hf.exe"
        if (Test-Path $candidate) {
            $HfExecutable = $candidate
        }
    }
}

if (-not $HfExecutable) {
    $candidate = "D:\github\talking-flower-voice\.venv\Scripts\hf.exe"
    if (Test-Path $candidate) {
        $HfExecutable = $candidate
    }
}

if (-not $HfExecutable -or -not (Test-Path $HfExecutable)) {
    throw "Cannot find hf.exe. Install it with 'python -m pip install -U huggingface_hub' or pass -HfExecutable."
}

$source = $PSScriptRoot

Write-Host "Using HF CLI: $HfExecutable"

& $HfExecutable auth whoami
if ($LASTEXITCODE -ne 0) {
    throw "Run 'hf auth login' first with a token that has Write permission."
}

& $HfExecutable repo create $RepoId `
    --type space `
    --sdk gradio `
    --flavor cpu-basic `
    --public `
    --exist-ok
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create the Hugging Face Space."
}

& $HfExecutable upload $RepoId $source . `
    --repo-type space `
    --exclude "deploy.ps1" `
    --exclude "run-local.ps1" `
    --exclude "__pycache__/*" `
    --commit-message "Create Tiny Qwen3 30M Chinese Gradio demo"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upload the Hugging Face Space files."
}

Write-Host "Space: https://huggingface.co/spaces/$RepoId"
