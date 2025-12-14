"""
Script para limpar arquivos de sessão bloqueados do Telegram
Use este script se você encontrar erros de "database is locked"
"""
import os
import sys
import glob

def clear_session(session_name: str = "telegram_session"):
    """Remove arquivos de sessão do Telegram"""
    sessions_dir = "sessions"
    
    if not os.path.exists(sessions_dir):
        print(f"❌ Diretório {sessions_dir} não existe.")
        return False
    
    # Buscar todos os arquivos relacionados à sessão
    session_patterns = [
        f"{session_name}.session",
        f"{session_name}.session-journal",
        f"{session_name}.session-*"
    ]
    
    files_removed = []
    
    for pattern in session_patterns:
        files = glob.glob(os.path.join(sessions_dir, pattern))
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    files_removed.append(os.path.basename(file_path))
                    print(f"✅ Removido: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️  Erro ao remover {os.path.basename(file_path)}: {e}")
    
    if files_removed:
        print(f"\n✅ {len(files_removed)} arquivo(s) de sessão removido(s) com sucesso!")
        print("⚠️  Você precisará autenticar novamente na próxima execução.")
        return True
    else:
        print("ℹ️  Nenhum arquivo de sessão encontrado para remover.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧹 Limpador de Sessão do Telegram")
    print("=" * 60)
    
    session_name = "telegram_session"
    if len(sys.argv) > 1:
        session_name = sys.argv[1]
    
    print(f"\n📁 Procurando arquivos de sessão: {session_name}")
    print("=" * 60)
    
    clear_session(session_name)

