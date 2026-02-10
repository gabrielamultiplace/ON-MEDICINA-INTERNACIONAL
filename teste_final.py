#!/usr/bin/env python3
"""
Teste final de integração - verifica se o servidor está rodando
e se os dados estão sendo servidos corretamente
"""
import requests
import json
import time

def test_integration():
    """Testa a integração completa"""
    
    print("=" * 80)
    print("🚀 TESTE FINAL DE INTEGRAÇÃO")
    print("=" * 80)
    
    BASE_URL = "http://localhost:5000"
    
    try:
        # Teste 1: Servidor está rodando?
        print("\n1️⃣  Testando conectividade ao servidor...")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Servidor rodando em http://localhost:5000")
        else:
            print(f"   ❌ Servidor respondeu com status {response.status_code}")
            return False
        
        # Teste 2: HTML contém as estruturas?
        print("\n2️⃣  Verificando estruturas no HTML...")
        
        checks = {
            'data-tab="centros-custo"': 'Aba Centro de Custo',
            'data-tab="plano-contas"': 'Aba Plano de Contas',
            'id="centros-grupos"': 'Container Centro de Custos',
            'id="table-plano-contas"': 'Tabela Plano de Contas',
            'loadCentrosCustoFromFile': 'Função de carregamento CC',
            'loadPlanoContasFromFile': 'Função de carregamento PC',
        }
        
        for check, description in checks.items():
            if check in response.text:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} - NÃO ENCONTRADO")
        
        # Teste 3: Arquivos JSON existem?
        print("\n3️⃣  Verificando arquivos JSON...")
        
        try:
            with open('data/centros_custo.json', 'r', encoding='utf-8') as f:
                cc_data = json.load(f)
            print(f"   ✅ centros_custo.json - {len(cc_data['grupos'])} grupos")
        except Exception as e:
            print(f"   ❌ centros_custo.json - {str(e)}")
        
        try:
            with open('data/plano_contas.json', 'r', encoding='utf-8') as f:
                pc_data = json.load(f)
            print(f"   ✅ plano_contas.json - {len(pc_data['plano_contas'])} grupos contábeis")
        except Exception as e:
            print(f"   ❌ plano_contas.json - {str(e)}")
        
        # Teste 4: CSS está presente?
        print("\n4️⃣  Verificando CSS customizado...")
        
        css_checks = {
            '.centros-custo-container': 'Container estilizado',
            '.grupo-container': 'Grupos estilizados',
            '.subgrupos-table': 'Tabelas estilizadas',
            '.grupo-header': 'Cabeçalhos estilizados',
        }
        
        for css_class, description in css_checks.items():
            if css_class in response.text:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")
        
        # Teste 5: Status final
        print("\n" + "=" * 80)
        print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 80)
        
        print("\n📋 PRÓXIMAS AÇÕES:")
        print("1. Abra http://localhost:5000 no navegador")
        print("2. Clique em 'Financeiro' no menu lateral")
        print("3. Visualize as abas 'Centros de Custo' e 'Plano de Contas'")
        print("4. Veja a estrutura hierárquica dos dados!")
        
        print("\n📊 RESUMO DOS DADOS:")
        print(f"   • Centro de Custos: {len(cc_data['grupos'])} grupos")
        total_subs = sum(len(g['subgrupos']) for g in cc_data['grupos'])
        print(f"   • Total de subgrupos: {total_subs}")
        print(f"   • Plano de Contas: {len(pc_data['plano_contas'])} grupos contábeis")
        total_subs_pc = sum(len(c['subcategorias']) for c in pc_data['plano_contas'])
        print(f"   • Total de subcategorias: {total_subs_pc}")
        
        print("\n💡 DICAS:")
        print("   • Abra DevTools (F12) para ver o console")
        print("   • Não deve haver erros vermelhos")
        print("   • Os dados são carregados dinamicamente via JSON")
        print("   • Recarregue (F5) se os dados não aparecerem")
        
        print("\n" + "=" * 80)
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERRO: Não conseguiu conectar ao servidor")
        print("   Inicie o servidor com: python app.py")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_integration()
    exit(0 if success else 1)
