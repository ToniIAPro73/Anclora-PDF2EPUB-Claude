# Anclora PDF2EPUB - Inicio Automatico con Selector de Carpeta
Add-Type -AssemblyName System.Windows.Forms

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "ANCLORA PDF2EPUB - SELECCIONAR CARPETA DEL PROYECTO" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Función para seleccionar carpeta
function Select-Folder {
    param([string]$Description)

    $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderBrowser.Description = $Description
    $folderBrowser.ShowNewFolderButton = $false
    $folderBrowser.SelectedPath = $PWD

    $result = $folderBrowser.ShowDialog()
    if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
        return $folderBrowser.SelectedPath
    }
    return $null
}

# Seleccionar carpeta del proyecto
Write-Host "Se abrira un selector para elegir la carpeta del proyecto..." -ForegroundColor Yellow
$projectFolder = Select-Folder -Description "Selecciona la carpeta del proyecto Anclora PDF2EPUB"

if ($projectFolder -eq $null) {
    Write-Host "No se selecciono ninguna carpeta. Saliendo..." -ForegroundColor Red
    exit 1
}

Write-Host "Carpeta seleccionada: $projectFolder" -ForegroundColor Green

# Verificar estructura
$backendPath = Join-Path $projectFolder "backend"
$frontendPath = Join-Path $projectFolder "frontend"
$venvPath = Join-Path $projectFolder "venv-py311"

if (!(Test-Path $backendPath) -or !(Test-Path $frontendPath)) {
    Write-Host "ERROR: No se encontraron las carpetas 'backend' y 'frontend'" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

$useVenv = Test-Path "$venvPath\Scripts\Activate.ps1"
if ($useVenv) {
    Write-Host "OK: Entorno virtual encontrado" -ForegroundColor Green
} else {
    Write-Host "AVISO: No se encontro entorno virtual" -ForegroundColor Yellow
}

# Verificar Docker
Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    $null = docker version 2>$null
    Write-Host "OK: Docker listo" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker no esta corriendo" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Configurar Redis
Write-Host "Configurando Redis..." -ForegroundColor Yellow
docker stop redis-anclora 2>$null | Out-Null
docker rm redis-anclora 2>$null | Out-Null

$null = docker run -d --name redis-anclora -p 6379:6379 redis:7-alpine redis-server --requirepass XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ --appendonly yes
Start-Sleep -Seconds 3

Write-Host "OK: Redis listo en puerto 6379" -ForegroundColor Green

# Crear scripts para terminales
$venvCmd = if ($useVenv) { "& '$venvPath\Scripts\Activate.ps1'" } else { "Write-Host 'Sin entorno virtual'" }

$backendScript = @"
Set-Location '$projectFolder'
$venvCmd
Set-Location backend
Write-Host 'BACKEND - Instalando dependencias...' -ForegroundColor Green
pip install -r requirements.txt
Write-Host 'BACKEND - Iniciando Flask...' -ForegroundColor Green
python main.py
"@

$frontendScript = @"
Set-Location '$frontendPath'
Write-Host 'FRONTEND - Instalando dependencias...' -ForegroundColor Blue
npm install
Write-Host 'FRONTEND - Iniciando Vite...' -ForegroundColor Blue
npm start
"@

$celeryScript = @"
Set-Location '$projectFolder'
$venvCmd
Set-Location backend
Start-Sleep -Seconds 15
Write-Host 'CELERY - Iniciando Worker...' -ForegroundColor Magenta
celery -A app.tasks.celery_app worker --loglevel=info --pool=eventlet
"@

# Guardar scripts temporales
$backendScript | Out-File -FilePath "$env:TEMP\backend.ps1" -Encoding UTF8
$frontendScript | Out-File -FilePath "$env:TEMP\frontend.ps1" -Encoding UTF8
$celeryScript | Out-File -FilePath "$env:TEMP\celery.ps1" -Encoding UTF8

# Abrir terminales
Write-Host ""
Write-Host "Abriendo 3 terminales..." -ForegroundColor Yellow

if (Get-Command "wt" -ErrorAction SilentlyContinue) {
    Start-Process "wt" -ArgumentList "new-tab", "--title", "Backend", "powershell", "-NoExit", "-File", "$env:TEMP\backend.ps1"
    Start-Sleep -Seconds 1
    Start-Process "wt" -ArgumentList "new-tab", "--title", "Frontend", "powershell", "-NoExit", "-File", "$env:TEMP\frontend.ps1"
    Start-Sleep -Seconds 1
    Start-Process "wt" -ArgumentList "new-tab", "--title", "Celery", "powershell", "-NoExit", "-File", "$env:TEMP\celery.ps1"
} else {
    Start-Process "powershell" -ArgumentList "-NoExit", "-File", "$env:TEMP\backend.ps1"
    Start-Process "powershell" -ArgumentList "-NoExit", "-File", "$env:TEMP\frontend.ps1"
    Start-Process "powershell" -ArgumentList "-NoExit", "-File", "$env:TEMP\celery.ps1"
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "TERMINALES ABIERTOS EN: $projectFolder" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:5178" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:5175" -ForegroundColor White
Write-Host "  Redis:    localhost:6379" -ForegroundColor White
Write-Host ""

Read-Host "Presiona Enter para cerrar"