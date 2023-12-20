try {
    Get-Command python -ErrorAction Stop
} catch {
    Write-Host "No Python found. Installing Python 3.12..."
    winget install -e --id Python.Python.3.12
}

try {
    Get-Command pip -ErrorAction Stop
} catch {
    Write-Host "No pip found. Installing..."
    py -m ensurepip --upgrade
}

pip install flake8
pip install requests
pip install bs4
pip install atomicwrites