param(
    [string]$RepoId = "richarddzh/tiny-qwen3-30m-zh-completion",
    [string]$Proxy = "http://127.0.0.1:10808"
)

$ErrorActionPreference = "Stop"

if ($Proxy) {
    $env:HTTP_PROXY = $Proxy
    $env:HTTPS_PROXY = $Proxy
    Remove-Item Env:ALL_PROXY -ErrorAction SilentlyContinue
}

$hf = Get-Command hf -ErrorAction Stop
$source = $PSScriptRoot

& $hf.Source auth whoami
if ($LASTEXITCODE -ne 0) {
    throw "Run 'hf auth login' first with a token that has Write permission."
}

& $hf.Source repo create $RepoId `
    --type space `
    --sdk gradio `
    --flavor cpu-basic `
    --public `
    --exist-ok
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create the Hugging Face Space."
}

& $hf.Source upload $RepoId $source . `
    --repo-type space `
    --exclude "deploy.ps1" `
    --exclude "run-local.ps1" `
    --exclude "__pycache__/*" `
    --commit-message "Create Tiny Qwen3 30M Chinese Gradio demo"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upload the Hugging Face Space files."
}

Write-Host "Space: https://huggingface.co/spaces/$RepoId"
