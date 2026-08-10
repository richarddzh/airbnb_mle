param(
    [string]$Proxy = "http://127.0.0.1:10808"
)

$ErrorActionPreference = "Stop"

if ($Proxy) {
    $env:HTTP_PROXY = $Proxy
    $env:HTTPS_PROXY = $Proxy
    Remove-Item Env:ALL_PROXY -ErrorAction SilentlyContinue
}

Push-Location $PSScriptRoot
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies."
    }

    python app.py
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start the local Gradio app."
    }
}
finally {
    Pop-Location
}
