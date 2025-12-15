"""
Script para obter o ID do canal DramaFlix
Funciona enviando uma mensagem de teste e capturando o ID
"""
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

async def get_dramaflix_channel_id():
    """Tenta obter o ID do canal DramaFlix"""
    print("=" * 60)
    print("🔍 Obtendo ID do Canal DramaFlix")
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
        "get_channel_id_session",
        bot_token=bot_token,
        api_id=api_id,
        api_hash=api_hash,
        workdir="sessions"
    )
    
    try:
        await bot_client.start()
        bot_info = await bot_client.get_me()
        print(f"🤖 Conectado como bot: @{bot_info.username}\n")
        
        print("📋 MÉTODO 1 - Usando link do Telegram (MAIS FÁCIL):")
        print("   1. Abra o canal DramaFlix no Telegram")
        print("   2. Clique em qualquer mensagem do canal")
        print("   3. Clique em 'Copiar link' ou 'Share'")
        print("   4. O link terá o formato: t.me/c/1234567890/123")
        print("   5. O número grande (1234567890) é o ID do canal")
        print("   6. Adicione -100 na frente: -1001234567890")
        print("   Exemplo: Se o link for t.me/c/1234567890/123")
        print("           O ID será: -1001234567890")
        print()
        
        print("📋 MÉTODO 2 - Usando @getidsbot:")
        print("   1. Adicione o bot @getidsbot ao canal DramaFlix")
        print("   2. O bot mostrará automaticamente o ID do canal")
        print()
        
        print("📋 MÉTODO 3 - Manualmente (se você é administrador):")
        print("   1. Abra o canal DramaFlix")
        print("   2. Vá em Configurações > Administradores")
        print("   3. Procure pelo bot @DoramaVideos_bot")
        print("   4. O ID pode aparecer nas informações")
        print()
        
        print("📋 MÉTODO 4 - Testando acesso direto:")
        print("   Vou tentar acessar o canal com diferentes formatos...\n")
        
        # Tentar diferentes formatos
        test_names = ["DramaFlix", "@DramaFlix", "dramaflix", "@dramaflix"]
        
        for test_name in test_names:
            try:
                chat = await bot_client.get_chat(test_name)
                print(f"✅ SUCESSO! Canal encontrado:")
                print(f"   Nome: {chat.title}")
                print(f"   ID: {chat.id}")
                if chat.username:
                    print(f"   Username: @{chat.username}")
                print(f"\n⚙️  Configure no .env:")
                print(f"   DRAMAFLEX_CHANNEL={chat.id}")
                return
            except Exception as e:
                error_str = str(e).lower()
                if "username" not in error_str and "not found" not in error_str:
                    print(f"   Tentativa com '{test_name}': {e}")
        
        print("❌ Não foi possível encontrar o canal automaticamente.")
        print("\n💡 SOLUÇÃO RECOMENDADA:")
        print("   1. Abra o canal DramaFlix no Telegram")
        print("   2. Copie o link de qualquer mensagem (t.me/c/ID/123)")
        print("   3. Extraia o ID do link e adicione -100 na frente")
        print("   4. Configure no .env: DRAMAFLEX_CHANNEL=-1001234567890")
        print("\n   Exemplo de link: t.me/c/1234567890/123")
        print("   ID extraído: 1234567890")
        print("   ID completo: -1001234567890")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot_client.stop()

if __name__ == "__main__":
    asyncio.run(get_dramaflix_channel_id())

