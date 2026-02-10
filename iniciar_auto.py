#!/usr/bin/env python3
"""
Script para iniciar o servidor com auto-reload
Reinicia automaticamente quando há mudanças nos arquivos
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)

class FileChangeHandler(FileSystemEventHandler):
    """Handler para detectar mudanças nos arquivos"""
    
    def __init__(self, on_change):
        self.on_change = on_change
        self.last_modified = time.time()
    
    def on_modified(self, event):
        """Chamado quando um arquivo é modificado"""
        if event.is_directory:
            return
        
        # Evitar múltiplos eventos para o mesmo arquivo
        current_time = time.time()
        if current_time - self.last_modified < 1:
            return
        
        self.last_modified = current_time
        
        # Ignorar alguns arquivos
        if event.src_path.endswith(('.pyc', '.db', '__pycache__')):
            return
        
        print(f"\n✓ Mudança detectada em: {event.src_path}")
        self.on_change()

def start_server():
    """Inicia o servidor Flask"""
    print("\n" + "="*60)
    print("  ON Medicina Internacional - Servidor com Auto-Reload")
    print("="*60 + "\n")
    
    print("✓ Iniciando servidor Flask...")
    print("  URL: http://localhost:5000")
    print("  Email: gabrielamultiplace@gmail.com")
    print("  Senha: @On2025@\n")
    
    # Iniciar servidor
    try:
        subprocess.run([sys.executable, 'app.py'], check=False)
    except KeyboardInterrupt:
        print("\n\n✓ Servidor interrompido")
        sys.exit(0)

def main():
    """Função principal"""
    # Verificar dependências
    try:
        import flask
    except ImportError:
        print("✓ Instalando Flask...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
    
    # Verificar se watchdog está disponível
    try:
        from watchdog.observers import Observer
        use_watchdog = True
    except ImportError:
        print("⚠ Watchdog não instalado - auto-reload desabilitado")
        use_watchdog = False
    
    # Iniciar servidor
    if not use_watchdog:
        # Modo simples sem watchdog
        start_server()
    else:
        # Modo com auto-reload
        event_handler = FileChangeHandler(start_server)
        observer = Observer()
        observer.schedule(event_handler, str(BASE_DIR), recursive=True)
        observer.start()
        
        try:
            start_server()
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == '__main__':
    main()
