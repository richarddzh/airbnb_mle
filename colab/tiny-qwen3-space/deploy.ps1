$ErrorActionPreference = "Stop"

$env:HTTP_PROXY = "http://localhost:10808"
$env:HTTPS_PROXY = "http://localhost:10808"
Remove-Item Env:ALL_PROXY -ErrorAction SilentlyContinue

$hf = "D:\github\talking-flower-voice\.venv\Scripts\hf.exe"
$repo = "richarddzh/tiny-qwen3-30m-completion"
$source = $PSScriptRoot

& $hf repo create $repo `
    --type space `
    --sdk gradio `
    --flavor cpu-basic `
    --public `
    --exist-ok

& $hf upload $repo $source . `
    --repo-type space `
    --exclude "deploy.ps1" `
    --exclude "__pycache__/*" `
    --commit-message "Create Tiny Qwen3 Gradio demo"

Write-Host "Space: https://huggingface.co/spaces/$repo"
