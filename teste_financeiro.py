#!/usr/bin/env python3
"""
Script para testar se o módulo financeiro está funcionando corretamente
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_financeiro_module():
    """Testa se o módulo financeiro está acessível e funcionando"""
    
    print("=" * 60)
    print("🧪 TESTE DO MÓDULO FINANCEIRO")
    print("=" * 60)
    
    try:
        # Teste 1: Acessar página principal
        print("\n1️⃣  Testando acesso à página principal...")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Página principal carregada com sucesso (status 200)")
            
            # Verificar se o módulo financeiro está no HTML
            if 'id="financeiro"' in response.text:
                print("   ✅ Seção financeiro encontrada no HTML")
            else:
                print("   ❌ Seção financeiro NÃO encontrada no HTML")
                return False
                
            # Verificar se as abas estão no HTML
            required_tabs = [
                'financeiro-tab-btn',
                'financeiro-tab-pane',
                'data-tab="dashboard"',
                'data-tab="centros-custo"',
                'data-tab="plano-contas"',
                'data-tab="fluxo-caixa"',
                'data-tab="bancos"',
                'data-tab="relatorios"'
            ]
            
            missing_items = []
            for item in required_tabs:
                if item not in response.text:
                    missing_items.append(item)
            
            if missing_items:
                print(f"   ⚠️  Elementos faltando: {missing_items}")
            else:
                print("   ✅ Todas as abas estão presentes no HTML")
                
            # Verificar se o JavaScript do módulo está presente
            if 'initFinanceiroModule' in response.text:
                print("   ✅ Função initFinanceiroModule encontrada")
            else:
                print("   ❌ Função initFinanceiroModule NÃO encontrada")
                
            if 'financeiroSection' in response.text:
                print("   ✅ Variável financeiroSection encontrada (variável corrigida)")
            else:
                print("   ❌ Variável financeiroSection NÃO encontrada")
                
        else:
            print(f"   ❌ Erro ao acessar página (status {response.status_code})")
            return False
            
        # Teste 2: Verificar API de dados financeiros (se existir)
        print("\n2️⃣  Testando endpoints de dados...")
        
        endpoints_to_test = [
            "/api/financeiro/dashboard",
            "/api/financeiro/centros-custo",
            "/api/financeiro/plano-contas",
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:
                    status = "✅ Existe" if response.status_code == 200 else "⚠️  Não existe"
                    print(f"   {status}: {endpoint}")
                else:
                    print(f"   ❌ Erro: {endpoint} (status {response.status_code})")
            except requests.exceptions.RequestException as e:
                print(f"   ⚠️  {endpoint}: {str(e)}")
        
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\n📋 INSTRUÇÕES PARA VER O MÓDULO FINANCEIRO:")
        print("1. Abra o navegador em: http://localhost:5000")
        print("2. Faça login se necessário")
        print("3. Clique no menu 'Financeiro'")
        print("4. Você verá 6 abas:")
        print("   - Dashboard (com KPIs e gráficos)")
        print("   - Centros de Custo")
        print("   - Plano de Contas")
        print("   - Fluxo de Caixa")
        print("   - Bancos")
        print("   - Relatórios")
        print("\n💡 Se alguma aba não carregar:")
        print("   - Abra o DevTools (F12)")
        print("   - Vá na aba 'Console'")
        print("   - Procure por mensagens de erro em vermelho")
        print("   - Reporte qualquer erro encontrado")
        print("=" * 60)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERRO: Não foi possível conectar ao servidor em {BASE_URL}")
        print("   Verifique se o servidor está rodando com: python app.py")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_financeiro_module()
    exit(0 if success else 1)
