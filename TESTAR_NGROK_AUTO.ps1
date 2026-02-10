
# Script para testar ngrok automaticamente a cada 2 minutos
# até conseguir conectar

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  NGROK AUTO-TEST - Aguardando expiração de sessão     ║" -ForegroundColor Cyan
Write-Host "║  Testará a cada 2 minutos automaticamente             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$tentativa = 0
$maxTentativas = 15  # 30 minutos (15 x 2 min)
$sucesso = $false

while ($tentativa -lt $maxTentativas -and -not $sucesso) {
    $tentativa++
    $horario = Get-Date -Format "HH:mm:ss"
    
    Write-Host "[$horario] Tentativa $tentativa/$maxTentativas..." -ForegroundColor Yellow
    
    # Tenta executar ngrok
    $output = & C:\ngrok-app\ngrok.exe http 8080 2>&1 | Out-String
    
    # Verifica se conectou (se não contém o erro ERR_NGROK_334)
    if ($output -notmatch "ERR_NGROK_334") {
        Write-Host "✓ SUCESSO! Ngrok conectou!" -ForegroundColor Green
        Write-Host $output -ForegroundColor Green
        $sucesso = $true
        break
    } else {
        Write-Host "✗ Sessão ainda está presa (ERR_NGROK_334)" -ForegroundColor Red
        Write-Host "  Próxima tentativa em 2 minutos..." -ForegroundColor Gray
        Write-Host ""
        
        # Aguarda 2 minutos
        Start-Sleep -Seconds 120
    }
}

if (-not $sucesso) {
    Write-Host ""
    Write-Host "Todas as $maxTentativas tentativas falharam." -ForegroundColor Red
    Write-Host "Tente novamente manualmente ou crie uma nova conta ngrok." -ForegroundColor Yellow
}
