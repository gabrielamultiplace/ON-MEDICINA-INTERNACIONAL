#!/bin/bash
# ============================================================================
# INICIAR SISTEMA COM ASAAS INTEGRADO
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    PLATAFORMA ON MEDICINA - ASAAS PAYMENT INTEGRATION         ║"
echo "║                     Versão 2.0                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "📋 Verificando ambiente..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

echo "✅ Python 3: $(python3 --version)"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale pip"
    exit 1
fi

echo "✅ pip: $(pip3 --version)"

# Instalar dependências se necessário
echo ""
echo "📦 Verificando dependências..."

if [ ! -d "venv" ]; then
    echo "🔨 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativar ambiente virtual
echo "🚀 Ativando ambiente virtual..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Instalar requirements
echo "📥 Instalando pacotes..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt -q
    echo "✅ Pacotes instalados"
else
    echo "⚠️  requirements.txt não encontrado"
    echo "📥 Instalando pacotes essenciais..."
    pip3 install flask requests -q
fi

# Verificar arquivos Asaas
echo ""
echo "📁 Verificando arquivos Asaas..."

FILES_REQUIRED=(
    "asaas_integration_v2.py"
    "asaas_config.py"
    "app.py"
    "index.html"
)

MISSING_FILES=0
for file in "${FILES_REQUIRED[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (FALTANDO)"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo "⚠️  Alguns arquivos estão faltando!"
    exit 1
fi

# Verificar API Key
echo ""
echo "🔑 Verificando API Key Asaas..."

if grep -q "aact_prod_" asaas_integration_v2.py; then
    echo "✅ API Key configurada"
else
    echo "⚠️  API Key não encontrada em asaas_integration_v2.py"
    echo "   Você pode configurar via variável de ambiente: ASAAS_API_KEY"
fi

# Testar conexão Asaas
echo ""
echo "🧪 Testando módulo Asaas..."

python3 -c "
from asaas_integration_v2 import AsaasIntegration
asaas = AsaasIntegration()
print('✅ Módulo Asaas carregado com sucesso')
" 2>/dev/null || echo "⚠️  Erro ao carregar módulo Asaas"

# Iniciar servidor
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 INICIANDO SERVIDOR FLASK                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "🚀 Servidor iniciando em http://localhost:5000"
echo ""
echo "Endpoints disponíveis:"
echo "  📱 Frontend: http://localhost:5000"
echo "  💳 Pagamento: POST http://localhost:5000/api/asaas/criar-pagamento"
echo "  📊 Status: GET http://localhost:5000/api/asaas/status-pagamento/<lead_id>"
echo "  🧪 Teste: GET http://localhost:5000/api/asaas/teste"
echo ""
echo "📚 Documentação:"
echo "  • ASAAS_INTEGRATION.md - Documentação completa"
echo "  • ASAAS_RESUMO_FINAL.md - Resumo de implementação"
echo ""
echo "🧪 Para testar em outro terminal:"
echo "  python3 test_asaas_integration.py"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Iniciar servidor Flask
python3 app.py
