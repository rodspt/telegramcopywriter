import asyncio
import time
import os
from pyrogram import Client
from pyrogram.session import Session
from pyrogram.raw.functions.help import GetConfig

async def fix_time_offset():
    """
    Tenta sincronizar o offset de tempo do Pyrogram com o servidor do Telegram.
    Isso ajuda a resolver o erro BadMsgNotification [17].
    """
    print("=" * 60)
    print("🔧 Corretor de Sincronização de Tempo Pyrogram")
    print("=" * 60)
    
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print("❌ Erro: TELEGRAM_API_ID e TELEGRAM_API_HASH não encontrados no ambiente.")
        return

    # Criar um cliente temporário apenas para obter o tempo do servidor
    client = Client(
        "temp_sync_session",
        api_id=int(api_id),
        api_hash=api_hash,
        workdir="sessions",
        in_memory=True
    )
    
    print("⏳ Tentando obter tempo do servidor do Telegram...")
    
    try:
        await client.connect()
        # Ao conectar, o Pyrogram tenta sincronizar o tempo internamente.
        # Podemos forçar uma chamada para garantir que o offset seja calculado.
        server_config = await client.invoke(GetConfig())
        
        # O Pyrogram armazena o offset globalmente na classe Session
        current_offset = Session.TIME_OFFSET
        print(f"✅ Conexão estabelecida!")
        print(f"⏰ Offset de tempo atual: {current_offset} segundos")
        
        if abs(current_offset) > 10:
            print(f"⚠️  Diferença significativa detectada ({current_offset}s).")
        else:
            print(f"ℹ️  Diferença de tempo pequena ({current_offset}s).")
            
        await client.disconnect()
        print("\n✅ Sincronização concluída com sucesso.")
        print("Agora você pode tentar rodar o main.py novamente.")
        
    except Exception as e:
        print(f"❌ Erro durante a sincronização: {e}")
        print("\n💡 Dica: Se o erro persistir, sincronize o relógio do seu computador (Host).")
        print("No Windows/WSL: w32tm /resync ou sudo ntpdate -s time.nist.gov")

if __name__ == "__main__":
    # Carregar .env se existir
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
        
    asyncio.run(fix_time_offset())
