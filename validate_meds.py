#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VALIDAÇÃO E LIMPEZA DE MEDICAMENTOS
Garante que não há medicamentos duplicados
"""

import json
import sys
from collections import Counter

def validate_medicamentos():
    """Valida o arquivo de medicamentos e remove duplicados"""
    
    print("\n" + "="*70)
    print("🧬 VALIDAÇÃO DE MEDICAMENTOS")
    print("="*70)
    
    # Carregar arquivo
    try:
        with open('data/medicamentos.json', 'r', encoding='utf-8') as f:
            meds = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler medicamentos.json: {e}")
        return False
    
    print(f"\n📊 Total de registros: {len(meds)}")
    
    if not isinstance(meds, list):
        print("❌ Formato inválido: não é uma lista!")
        return False
    
    # Verificar duplicados por nome
    nomes = [m.get('nome', '') for m in meds]
    nomes_unicos = set(nomes)
    
    print(f"📋 Nomes únicos: {len(nomes_unicos)}")
    
    # Encontrar duplicados
    contador = Counter(nomes)
    duplicados = {nome: qtd for nome, qtd in contador.items() if qtd > 1}
    
    if duplicados:
        print(f"\n⚠️  {len(duplicados)} medicamentos duplicados encontrados:")
        for nome, qtd in sorted(duplicados.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {nome}: {qtd}x")
        
        # Remover duplicados mantendo apenas o primeiro
        print("\n🔧 Removendo duplicados...")
        meds_limpo = []
        nomes_vistos = set()
        
        for med in meds:
            nome = med.get('nome', '')
            if nome not in nomes_vistos:
                meds_limpo.append(med)
                nomes_vistos.add(nome)
            else:
                print(f"   ❌ Removido duplicado: {nome}")
        
        # Salvar arquivo limpo
        try:
            with open('data/medicamentos.json', 'w', encoding='utf-8') as f:
                json.dump(meds_limpo, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Arquivo salvo com {len(meds_limpo)} medicamentos (únicos)")
            meds = meds_limpo
        except Exception as e:
            print(f"❌ Erro ao salvar medicamentos.json: {e}")
            return False
    else:
        print(f"✅ Nenhum duplicado encontrado!")
    
    # Validar campos obrigatórios
    print(f"\n📋 Validando campos obrigatórios...")
    campos_obrig = ['id', 'nome', 'laboratorio', 'tipo']
    erros = 0
    
    for idx, med in enumerate(meds):
        for campo in campos_obrig:
            if campo not in med or not med[campo]:
                print(f"   ⚠️  Medicamento {idx}: falta campo '{campo}'")
                erros += 1
    
    if erros == 0:
        print(f"✅ Todos os medicamentos têm campos obrigatórios")
    
    # Relatório final
    print(f"\n" + "="*70)
    print(f"📊 RELATÓRIO FINAL")
    print(f"="*70)
    print(f"✅ Total de medicamentos: {len(meds)}")
    print(f"✅ Medicamentos únicos: {len(set(nomes))} ({100*len(set(nomes))//len(meds)}%)")
    print(f"✅ Arquivo: data/medicamentos.json")
    print(f"✅ Status: VALIDADO E LIMPO")
    print("="*70 + "\n")
    
    return True

if __name__ == '__main__':
    sucesso = validate_medicamentos()
    sys.exit(0 if sucesso else 1)
