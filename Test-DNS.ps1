# PowerShell Script para Verificar DNS e Conectividade
# Uso: .\Test-DNS.ps1

param(
    [string]$Domain = "app.onmedicinainternacional.com",
    [string]$ExpectedIP = "186.232.133.253",
    [int]$Port = 5000
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE DE DNS - app.onmedicinainternacional.com" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$TestResults = @()

# Test 1: DNS Resolution
Write-Host "🔍 1. RESOLUÇAO DE DNS..." -ForegroundColor Yellow
$DnsResult = $null
try {
    $DnsResult = (Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop).IPAddress | Select-Object -First 1
    if ($DnsResult -eq $ExpectedIP) {
        Write-Host "   ✅ DNS RESOLVIDO CORRETAMENTE" -ForegroundColor Green
        Write-Host "      Nome: $Domain" -ForegroundColor Green
        Write-Host "      IP Resolvido: $DnsResult" -ForegroundColor Green
        Write-Host "      IP Esperado: $ExpectedIP" -ForegroundColor Green
        $TestResults += "DNS-OK"
    } elseif ($DnsResult) {
        Write-Host "   ⚠️  DNS RESOLVIDO, MAS IP DIFERENTE" -ForegroundColor Yellow
        Write-Host "      IP Resolvido: $DnsResult" -ForegroundColor Yellow
        Write-Host "      IP Esperado: $ExpectedIP" -ForegroundColor Yellow
        Write-Host "      Possível causa: Propagação DNS ainda em andamento" -ForegroundColor Yellow
        $TestResults += "DNS-DIFFERENT"
    } else {
        Write-Host "   ❌ ERRO AO RESOLVER DNS" -ForegroundColor Red
        $TestResults += "DNS-FAILED"
    }
} catch {
    Write-Host "   ❌ DNS NÃO RESOLUCIONADO" -ForegroundColor Red
    Write-Host "      Erro: $_" -ForegroundColor Red
    Write-Host "      Possível causa: DNS ainda não propagou (aguarde 15 min - 48h)" -ForegroundColor Yellow
    $TestResults += "DNS-ERROR"
}
Write-Host ""

# Test 2: Ping
Write-Host "📡 2. TESTE DE PING..." -ForegroundColor Yellow
try {
    $PingResult = Test-Connection -ComputerName $Domain -Count 1 -ErrorAction Stop
    Write-Host "   ✅ PING SUCESSO" -ForegroundColor Green
    Write-Host "      IP: $($PingResult.IPV4Address)" -ForegroundColor Green
    Write-Host "      Tempo: $($PingResult.ResponseTime)ms" -ForegroundColor Green
    $TestResults += "PING-OK"
} catch {
    Write-Host "   ❌ PING FALHOU" -ForegroundColor Red
    Write-Host "      Erro: $_" -ForegroundColor Red
    Write-Host "      Possível causa: Firewall bloqueando ICMP" -ForegroundColor Yellow
    $TestResults += "PING-FAILED"
}
Write-Host ""

# Test 3: HTTP Port Connectivity
Write-Host "🌐 3. CONECTIVIDADE HTTP (Porta 5000)..." -ForegroundColor Yellow
try {
    $Response = Invoke-WebRequest -Uri "http://$Domain`:$Port/" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    if ($Response.StatusCode -eq 200) {
        Write-Host "   ✅ SERVIDOR RESPONDENDO" -ForegroundColor Green
        Write-Host "      URL: http://$Domain`:$Port/" -ForegroundColor Green
        Write-Host "      Status: $($Response.StatusCode) $($Response.StatusDescription)" -ForegroundColor Green
        $TestResults += "HTTP-OK"
    } else {
        Write-Host "   ⚠️  SERVIDOR RESPONDEU COM STATUS: $($Response.StatusCode)" -ForegroundColor Yellow
        $TestResults += "HTTP-WARN"
    }
} catch {
    Write-Host "   ❌ NÃO CONSEGUIU CONECTAR" -ForegroundColor Red
    Write-Host "      URL: http://$Domain`:$Port/" -ForegroundColor Red
    Write-Host "      Erro: $_" -ForegroundColor Red
    Write-Host "      Possível causa:" -ForegroundColor Yellow
    Write-Host "        - Flask não está rodando (executar: python app.py)" -ForegroundColor Yellow
    Write-Host "        - Firewall bloqueando porta $Port" -ForegroundColor Yellow
    Write-Host "        - Port forwarding não configurado no router" -ForegroundColor Yellow
    $TestResults += "HTTP-FAILED"
}
Write-Host ""

# Test 4: HTTPS Port (443)
Write-Host "🔒 4. HTTPS (Porta 443)..." -ForegroundColor Yellow
try {
    $Response = Invoke-WebRequest -Uri "https://$Domain/" -UseBasicParsing -TimeoutSec 10 -SkipCertificateCheck -ErrorAction Stop
    Write-Host "   ✅ HTTPS RESPONDENDO" -ForegroundColor Green
    Write-Host "      Status: $($Response.StatusCode)" -ForegroundColor Green
    $TestResults += "HTTPS-OK"
} catch {
    if ($_ -match "SSL|certificate|443") {
        Write-Host "   [PENDENTE] HTTPS NAO CONFIGURADO AINDA" -ForegroundColor Yellow
        Write-Host "      Proxima etapa: Instalar SSL certificate (Lets Encrypt)" -ForegroundColor Yellow
        $TestResults += "HTTPS-PENDING"
    } else {
        Write-Host "   ❌ NÃO CONSEGUIU CONECTAR EM HTTPS" -ForegroundColor Red
        Write-Host "      Erro: $($_ | Select-Object -First 1)" -ForegroundColor Red
        $TestResults += "HTTPS-FAILED"
    }
}
Write-Host ""

# Test 5: Check Local Services
Write-Host "⚙️  5. SERVIÇOS LOCAIS..." -ForegroundColor Yellow
$PythonRunning = Get-Process python -ErrorAction SilentlyContinue
if ($PythonRunning) {
    Write-Host "   ✅ PYTHON RODANDO" -ForegroundColor Green
    Write-Host "      Processos: $($PythonRunning.Count)" -ForegroundColor Green
    $TestResults += "PYTHON-OK"
} else {
    Write-Host "   ❌ PYTHON NÃO ESTÁ RODANDO" -ForegroundColor Red
    Write-Host "      Execute: cd 'c:\Users\Gabriela Resende\Documents\Plataforma ON'; python app.py" -ForegroundColor Yellow
    $TestResults += "PYTHON-NOT-RUNNING"
}

$LocalServer = Test-NetConnection -ComputerName localhost -Port 5000 -WarningAction SilentlyContinue
if ($LocalServer.TcpTestSucceeded) {
    Write-Host "   ✅ SERVIDOR LOCAL (localhost:5000) RESPONDENDO" -ForegroundColor Green
    $TestResults += "LOCAL-OK"
} else {
    Write-Host "   ❌ SERVIDOR LOCAL NÃO RESPONDENDO" -ForegroundColor Red
    $TestResults += "LOCAL-FAILED"
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DOS TESTES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$SuccessCount = @($TestResults | Where-Object { $_ -match "OK" }).Count
$TotalTests = $TestResults.Count

Write-Host ""
Write-Host "Testes Bem-Sucedidos: $SuccessCount / $TotalTests" -ForegroundColor Cyan
Write-Host ""

# Recommendations
Write-Host "📋 RECOMENDAÇÕES:" -ForegroundColor Cyan
Write-Host ""

if ($TestResults -contains "DNS-ERROR" -or $TestResults -contains "DNS-FAILED") {
    Write-Host "1. ❌ DNS Não Está Configurado" -ForegroundColor Red
    Write-Host "   - Abrir: CONFIGURACAO_DNS.md" -ForegroundColor Yellow
    Write-Host "   - Adicionar registro A no registrador para 'app' apontando para 186.232.133.253" -ForegroundColor Yellow
    Write-Host "   - Aguardar propagação DNS (15 min - 48 horas)" -ForegroundColor Yellow
    Write-Host ""
}

if ($TestResults -contains "PYTHON-NOT-RUNNING") {
    Write-Host "2. ❌ Flask Não Está Rodando" -ForegroundColor Red
    Write-Host "   - Execute:" -ForegroundColor Yellow
    Write-Host "     cd 'c:\Users\Gabriela Resende\Documents\Plataforma ON'" -ForegroundColor Green
    Write-Host "     python app.py" -ForegroundColor Green
    Write-Host ""
}

if ($TestResults -contains "HTTP-FAILED") {
    Write-Host "3. ❌ Servidor HTTP Não Acessível" -ForegroundColor Red
    Write-Host "   - Possíveis causas:" -ForegroundColor Yellow
    Write-Host "     a) Firewall bloqueando (abrir porta 5000 ou 80)" -ForegroundColor Yellow
    Write-Host "     b) Router não fazendo port forwarding (abrir portas 80/443)" -ForegroundColor Yellow
    Write-Host "     c) Flask não está rodando (veja item 2)" -ForegroundColor Yellow
    Write-Host ""
}

if ($TestResults -contains "HTTPS-NOT-CONFIGURED") {
    Write-Host "4. ⏳ SSL Certificate Não Configurado" -ForegroundColor Yellow
    Write-Host "   - Próxima etapa após DNS funcionar:" -ForegroundColor Yellow
    Write-Host "   - Ver: DEPLOYMENT_GUIDE.md (Fase 3)" -ForegroundColor Yellow
    Write-Host "   - Usar Let's Encrypt (grátis)" -ForegroundColor Yellow
    Write-Host ""
}

if (@($TestResults | Where-Object { $_ -match "OK" }).Count -eq $TotalTests) {
    Write-Host "✅ TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    Write-Host "   Próxima etapa: Instalar SSL e configurar nginx" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Para mais informações, consulte: CONFIGURACAO_DNS.md" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Exit with appropriate code
if (@($TestResults | Where-Object { $_ -match "FAILED" }).Count -gt 0) {
    exit 1
} else {
    exit 0
}
