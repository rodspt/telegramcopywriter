"""
Script de teste para verificar conexão com Telegram fora do Docker
Use este script para testar se o problema é específico do Docker
"""
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

async def test_connection():
    """Testa conexão com Telegram"""
    print("=" * 60)
    print("🧪 Teste de Conexão com Telegram")
    print("=" * 60)
    
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print("❌ Erro: TELEGRAM_API_ID e TELEGRAM_API_HASH devem estar configurados!")
        return
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ Erro: TELEGRAM_API_ID deve ser um número!")
        return
    
    # Verificar se está em Docker
    if os.path.exists('/.dockerenv'):
        print("🐳 Executando em container Docker")
    else:
        print("💻 Executando no sistema host")
    
    # Criar cliente de teste
    client = Client(
        "test_connection_session",
        api_id=api_id,
        api_hash=api_hash,
        workdir="sessions",
        no_updates=True
    )
    
    try:
        print("\n🔄 Tentando conectar...")
        await asyncio.sleep(2.0)  # Delay antes de conectar
        
        await client.start()
        user_info = await client.get_me()
        
        print("✅ Conexão bem-sucedida!")
        print(f"👤 Usuário: {user_info.first_name}")
        if user_info.username:
            print(f"   Username: @{user_info.username}")
        
    except Exception as e:
        error_str = str(e).lower()
        print(f"\n❌ Erro ao conectar: {e}")
        
        if "msg_id is too high" in error_str or "client time has to be synchronized" in error_str:
            print("\n💡 Este é um erro de sincronização de tempo.")
            print("   Se você está executando no host (fora do Docker),")
            print("   tente sincronizar o tempo:")
            print("   sudo ntpdate -s time.nist.gov")
        
    finally:
        try:
            if client.is_connected:
                await client.stop()
        except:
            pass  # Ignorar erros ao parar o cliente

if __name__ == "__main__":
    asyncio.run(test_connection())

