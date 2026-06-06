# Run the API locally from app/backend (PowerShell)
Set-Location $PSScriptRoot
uvicorn main:app --app-dir src --reload --port 8000
