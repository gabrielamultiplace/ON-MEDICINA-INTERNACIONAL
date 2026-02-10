#!/usr/bin/env python
"""
Servidor Flask - Cannabis Medicinal
Mantém o servidor rodando com reinicialização automática em caso de erro
"""

import sys
import time
import subprocess

print("\n" + "="*70)
print("🧬 PLATAFORMA ON - SERVIDOR FLASK")
print("="*70)
print("\nIniciando servidor na porta 5000...")
print("Acesse: http://localhost:5000")
print("\nPressione CTRL+C para parar o servidor\n")

max_retries = 5
retry_count = 0

while retry_count < max_retries:
    try:
        # Start Flask app
        result = subprocess.call([sys.executable, "app.py"])
        
        if result == 0:
            print("\n✓ Servidor encerrado normalmente")
            break
        else:
            retry_count += 1
            print(f"\n⚠ Servidor encerrou inesperadamente (tentativa {retry_count}/{max_retries})")
            
            if retry_count < max_retries:
                print("Reiniciando em 3 segundos...")
                time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n✓ Servidor parado pelo usuário")
        sys.exit(0)
    except Exception as e:
        retry_count += 1
        print(f"\n✗ Erro: {e}")
        
        if retry_count < max_retries:
            print(f"Tentando novamente ({retry_count}/{max_retries})...")
            time.sleep(2)

if retry_count >= max_retries:
    print(f"\n✗ Servidor falhou após {max_retries} tentativas")
    sys.exit(1)

print("\n" + "="*70)
print("Servidor finalizado")
print("="*70)
