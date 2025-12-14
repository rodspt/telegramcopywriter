"""
Script de migração para adicionar a coluna image_path na tabela videos
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://telegram_user:telegram_pass@postgres:5432/telegram_videos")

def migrate():
    """Adiciona a coluna image_path na tabela videos"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Verificar se a coluna já existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'videos' 
                AND column_name = 'image_path'
            """))
            
            row = result.fetchone()
            if row:
                print("✅ A coluna image_path já existe. Nenhuma migração necessária.")
                return
            
            # Adicionar a coluna image_path
            conn.execute(text("ALTER TABLE videos ADD COLUMN image_path VARCHAR"))
            conn.commit()
            print("✅ Migração concluída com sucesso! A coluna image_path foi adicionada.")
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 Migração: Adicionar coluna image_path")
    print("=" * 60)
    migrate()

