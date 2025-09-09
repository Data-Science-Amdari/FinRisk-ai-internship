# scripts/update_deps.ps1

Write-Host "Step 1: Compiling requirements..."
pip-compile requirements.in -o requirements.txt
pip-compile requirements_dev.in -o requirements_dev.txt

Write-Host "Step 2: Installing dependencies..."
pip install -r requirements_dev.txt

Write-Host "Step 3: Freezing environment..."
pip freeze > requirements-freeze.txt

Write-Host "All done! Your environment is updated and frozen."
