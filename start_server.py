#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Servidor Flask robusto com tratamento de erros
"""

import sys
import traceback
from app import app

if __name__ == '__main__':
    try:
        print("\n" + "="*70)
        print("🚀 INICIANDO SERVIDOR FLASK")
        print("="*70)
        print("Endereço: http://localhost:5000")
        print("="*70 + "\n")
        
        # Iniciar servidor
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"\n❌ ERRO AO INICIAR SERVIDOR:")
        print(f"   {str(e)}")
        traceback.print_exc()
        sys.exit(1)
