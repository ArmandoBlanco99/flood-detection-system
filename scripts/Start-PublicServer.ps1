# ============================================
# Start the application with Cloudflare Tunnel
# ============================================

param(
    [switch]$NoTunnel = $false
)

Write-Host ""
Write-Host "🌊 Sistema de Alertas de Inundaciones - CDMX" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check that the script is in the expected directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$srcPath = Join-Path $scriptPath "..\src"

if (!(Test-Path $srcPath)) {
    Write-Host "❌ Error: No se encontró la carpeta 'src'" -ForegroundColor Red
    exit 1
}

# Function to start Flask
function Start-Flask {
    Write-Host "[1/2] Iniciando servidor Flask..." -ForegroundColor Green
    Write-Host "      Puerto: 5000" -ForegroundColor Gray
    Write-Host ""
    
    $flaskProcess = Start-Process -FilePath "python" -ArgumentList "$srcPath\flask_server.py" -PassThru -NoNewWindow
    Write-Host "✅ Flask iniciado (PID: $($flaskProcess.Id))" -ForegroundColor Green
    return $flaskProcess
}

# Function to start Cloudflare Tunnel
function Start-CloudflareTunnel {
    Write-Host ""
    Write-Host "[2/2] Iniciando Cloudflare Tunnel..." -ForegroundColor Green
    Write-Host ""
    
    # Check that cloudflared is installed
    $cloudflaredPath = Get-Command cloudflared -ErrorAction SilentlyContinue
    if (!$cloudflaredPath) {
        Write-Host "❌ Error: cloudflared no está instalado o no está en el PATH" -ForegroundColor Red
        Write-Host "   Descárgalo desde: https://github.com/cloudflare/cloudflare-warp/releases" -ForegroundColor Yellow
        return $null
    }
    
    Write-Host "Ejecutando: cloudflared tunnel run sistema-inundaciones" -ForegroundColor Gray
    
    $tunnelProcess = Start-Process -FilePath "cloudflared" -ArgumentList "tunnel", "run", "sistema-inundaciones" -PassThru -NoNewWindow
    Write-Host "✅ Tunnel iniciado (PID: $($tunnelProcess.Id))" -ForegroundColor Green
    return $tunnelProcess
}

# Start the processes
$flaskProc = Start-Flask

if (!$NoTunnel) {
    $tunnelProc = Start-CloudflareTunnel
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ ¡Todo está listo!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (!$NoTunnel) {
    Write-Host "🌐 Tu aplicación está disponible en:" -ForegroundColor Cyan
    Write-Host "   https://sistema-inundaciones.midominio.com" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   (La URL exacta aparecerá en la ventana de Cloudflare)" -ForegroundColor Gray
} else {
    Write-Host "🌐 Tu aplicación está disponible en:" -ForegroundColor Cyan
    Write-Host "   http://localhost:5000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Procesos activos:" -ForegroundColor Cyan
Write-Host "   Flask: PID $($flaskProc.Id)" -ForegroundColor Gray
if ($tunnelProc) {
    Write-Host "   Cloudflare: PID $($tunnelProc.Id)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Para detener:" -ForegroundColor Cyan
Write-Host "   Opción 1: Presiona Ctrl+C en ambas ventanas" -ForegroundColor Gray
Write-Host "   Opción 2: Ejecuta 'Stop-Process -Id $($flaskProc.Id), $($tunnelProc.Id)'" -ForegroundColor Gray
Write-Host ""

# Keep the script running
while ($flaskProc.HasExited -eq $false) {
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "❌ Flask se ha detenido" -ForegroundColor Red
