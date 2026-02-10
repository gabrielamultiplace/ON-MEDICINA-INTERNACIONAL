#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LIMPEZA DE MEDICAMENTOS - Remove duplicados e reseta localStorage
"""

import json
import os

def clean_medicamentos():
    print("\n" + "="*70)
    print("🧬 LIMPEZA DE MEDICAMENTOS")
    print("="*70)
    
    # Ler arquivo original
    with open('data/medicamentos.json', 'r', encoding='utf-8') as f:
        meds = json.load(f)
    
    print(f"\n📊 Total atual: {len(meds)} medicamentos")
    
    # Se tem mais de 20, limpar duplicados
    if len(meds) > 20:
        print("⚠️  Detectado: Mais de 20 medicamentos!")
        print("🔧 Removendo duplicados...")
        
        # Manter apenas medicamentos únicos por nome
        vistos = {}
        meds_limpos = []
        
        for med in meds:
            nome = med.get('nome', '')
            if nome not in vistos:
                vistos[nome] = True
                meds_limpos.append(med)
            else:
                print(f"   ❌ Removido duplicado: {nome}")
        
        # Se ainda tem muitos (mais de 30), manter apenas os 20 primeiros
        if len(meds_limpos) > 30:
            print(f"\n⚠️  Ainda temos {len(meds_limpos)}, mantendo apenas os 20 primeiros...")
            meds_limpos = meds_limpos[:20]
        
        # Salvar
        with open('data/medicamentos.json', 'w', encoding='utf-8') as f:
            json.dump(meds_limpos, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Arquivo salvo com {len(meds_limpos)} medicamentos únicos")
    else:
        print(f"✅ Arquivo OK com {len(meds)} medicamentos")
    
    # Criar script de limpeza do localStorage
    print("\n📝 Criando script de limpeza do localStorage...")
    
    cleanup_script = """
    <script>
    // Limpar localStorage de medicamentos
    localStorage.removeItem('medicamentos');
    console.log('✅ localStorage limpo!');
    location.reload();
    </script>
    """
    
    with open('cleanup_localstorage.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Limpeza de Cache</title>
</head>
<body>
    <h1>Limpando cache local...</h1>
    <p>Aguarde...</p>
    <script>
        localStorage.removeItem('medicamentos');
        sessionStorage.clear();
        console.log('✅ Cache limpo!');
        alert('✅ Cache limpo com sucesso!\\n\\nVocê será redirecionado para a página principal.');
        window.location.href = '/';
    </script>
</body>
</html>
""")
    
    print("✅ Arquivo cleanup_localstorage.html criado")
    
    print(f"\n" + "="*70)
    print("INSTRUÇÕES:")
    print("="*70)
    print("1. Acesse http://localhost:5000/cleanup_localstorage.html")
    print("   OU")
    print("2. Abra DevTools (F12) > Console e execute:")
    print("   localStorage.removeItem('medicamentos');")
    print("   location.reload();")
    print("="*70 + "\n")
    
    return True

if __name__ == '__main__':
    clean_medicamentos()
