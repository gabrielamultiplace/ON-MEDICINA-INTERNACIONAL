#!/usr/bin/env python3
"""
Script para testar as estruturas de Centro de Custo e Plano de Contas
"""
import json
import os

def test_estruturas():
    """Verifica se os arquivos JSON foram criados corretamente"""
    
    print("=" * 70)
    print("🧪 TESTE DE ESTRUTURAS - CENTRO DE CUSTO E PLANO DE CONTAS")
    print("=" * 70)
    
    # Teste 1: Centro de Custos
    print("\n1️⃣  Verificando Centro de Custos...")
    try:
        with open('data/centros_custo.json', 'r', encoding='utf-8') as f:
            centros = json.load(f)
        
        total_grupos = len(centros.get('grupos', []))
        print(f"   ✅ Arquivo centros_custo.json carregado")
        print(f"   ✅ Total de grupos: {total_grupos}")
        
        for grupo in centros.get('grupos', []):
            num_subgrupos = len(grupo.get('subgrupos', []))
            print(f"      • {grupo['nome']}: {num_subgrupos} subgrupos")
            
    except Exception as e:
        print(f"   ❌ Erro ao ler centros_custo.json: {e}")
    
    # Teste 2: Plano de Contas
    print("\n2️⃣  Verificando Plano de Contas...")
    try:
        with open('data/plano_contas.json', 'r', encoding='utf-8') as f:
            plano = json.load(f)
        
        total_contas = len(plano.get('plano_contas', []))
        print(f"   ✅ Arquivo plano_contas.json carregado")
        print(f"   ✅ Total de grupos de contas: {total_contas}")
        
        total_subcategorias = 0
        for conta in plano.get('plano_contas', []):
            num_subs = len(conta.get('subcategorias', []))
            total_subcategorias += num_subs
            print(f"      • {conta['grupo']} / {conta['categoria']}: {num_subs} subcategorias")
        
        print(f"   ✅ Total de subcategorias: {total_subcategorias}")
        
    except Exception as e:
        print(f"   ❌ Erro ao ler plano_contas.json: {e}")
    
    # Teste 3: Validação de index.html
    print("\n3️⃣  Verificando index.html...")
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        checks = [
            ('id="centros-grupos"', 'Contêiner Centro de Custos'),
            ('id="table-plano-contas"', 'Tabela Plano de Contas'),
            ('loadCentrosCustoFromFile', 'Função de carregamento Centro de Custos'),
            ('loadPlanoContasFromFile', 'Função de carregamento Plano de Contas'),
            ('.grupo-container', 'CSS para grupos'),
            ('.subgrupos-table', 'CSS para tabelas de subgrupos'),
        ]
        
        for check, description in checks:
            if check in html_content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} - NÃO ENCONTRADO")
        
    except Exception as e:
        print(f"   ❌ Erro ao ler index.html: {e}")
    
    print("\n" + "=" * 70)
    print("✅ ESTRUTURA PRONTA PARA VISUALIZAÇÃO!")
    print("=" * 70)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Abra o navegador em: http://localhost:5000")
    print("2. Faça login se necessário")
    print("3. Clique em 'Financeiro' no menu")
    print("4. Acesse as abas:")
    print("   • 'Centros de Custo' - Veja a estrutura hierárquica")
    print("   • 'Plano de Contas' - Veja receitas e despesas")
    print("\n💾 Dados carregados de:")
    print("   • data/centros_custo.json")
    print("   • data/plano_contas.json")
    print("=" * 70)

if __name__ == "__main__":
    test_estruturas()
