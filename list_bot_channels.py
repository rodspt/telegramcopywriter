"""
Script para listar canais que o bot tem acesso (para encontrar o ID do DramaFlix)
"""
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

async def list_bot_channels():
    """Lista canais que o bot tem acesso"""
    print("=" * 60)
    print("🤖 Listando Canais Acessíveis pelo Bot")
    print("=" * 60)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não está configurado!")
        return
    
    if not api_id or not api_hash:
        print("❌ Erro: TELEGRAM_API_ID e TELEGRAM_API_HASH são necessários!")
        return
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ Erro: TELEGRAM_API_ID deve ser um número!")
        return
    
    # Criar cliente bot
    bot_client = Client(
        "bot_list_channels_session",
        bot_token=bot_token,
        api_id=api_id,
        api_hash=api_hash,
        workdir="sessions"
    )
    
    try:
        await bot_client.start()
        bot_info = await bot_client.get_me()
        print(f"🤖 Conectado como bot: @{bot_info.username}\n")
        
        print("⚠️  IMPORTANTE: Bots não podem usar get_dialogs()")
        print("   Você precisa informar o ID do canal diretamente.\n")
        print("💡 Para encontrar o ID do canal DramaFlix:")
        print("   1. Adicione o bot @DoramaVideos_bot como administrador do canal")
        print("   2. Use um bot como @userinfobot para obter o ID")
        print("   3. Ou use a API do Telegram para obter o ID")
        print("\n📝 Formato do ID de canal:")
        print("   - Canais privados: -1001234567890 (começa com -100)")
        print("   - Grupos: -1234567890")
        print("   - Canais públicos: use @username (ex: @DramaFlix)")
        print("\n⚙️  Configure no .env:")
        print("   DRAMAFLEX_CHANNEL=-1001234567890  # Substitua pelo ID real")
        
        # Tentar alguns IDs comuns ou sugerir como obter
        print("\n" + "=" * 60)
        print("💡 Dica: Para obter o ID do canal:")
        print("   1. Adicione o bot @userinfobot ao canal")
        print("   2. Envie qualquer mensagem no canal")
        print("   3. O bot responderá com o ID do canal")
        print("   4. Use esse ID no DRAMAFLEX_CHANNEL")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot_client.stop()

if __name__ == "__main__":
    asyncio.run(list_bot_channels())

