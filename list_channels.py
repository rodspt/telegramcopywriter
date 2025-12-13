import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.types import Chat

# Carregar variáveis de ambiente
load_dotenv()

async def list_channels():
    """Lista todos os canais que o usuário faz parte"""
    print("=" * 60)
    print("📱 Listando Canais do Telegram")
    print("=" * 60)
    
    # Obter credenciais do Telegram
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
    
    # Conectar ao Telegram
    client = Client(
        "telegram_session",
        api_id=api_id,
        api_hash=api_hash,
        workdir="sessions"
    )
    
    try:
        await client.start()
        print("✅ Conectado ao Telegram com sucesso!\n")
        
        print("🔍 Buscando canais e grupos...\n")
        
        channels = []
        groups = []
        all_chats = []
        
        # Buscar todos os diálogos
        async for dialog in client.get_dialogs():
            chat = dialog.chat
            chat_info = {
                'id': chat.id,
                'title': chat.title,
                'username': chat.username if chat.username else None,
                'type': chat.type.name if hasattr(chat.type, 'name') else str(chat.type),
                'is_broadcast': getattr(chat, 'is_broadcast', False),
                'is_verified': getattr(chat, 'is_verified', False),
                'is_scam': getattr(chat, 'is_scam', False),
                'is_fake': getattr(chat, 'is_fake', False)
            }
            
            all_chats.append(chat_info)
            
            # Separar canais e grupos
            if chat.type.name == "CHANNEL":
                channels.append(chat_info)
            elif chat.type.name in ["GROUP", "SUPERGROUP"]:
                groups.append(chat_info)
        
        # Ordenar por nome (tratando casos onde title pode ser None)
        channels.sort(key=lambda x: (x['title'] or '').lower())
        groups.sort(key=lambda x: (x['title'] or '').lower())
        all_chats.sort(key=lambda x: (x['title'] or '').lower())
        
        print("=" * 60)
        print(f"📊 Estatísticas:")
        print(f"   Total de chats: {len(all_chats)}")
        print(f"   Canais: {len(channels)}")
        print(f"   Grupos: {len(groups)}")
        print("=" * 60)
        print()
        
        # Mostrar canais
        if channels:
            print("📺 CANAIS:")
            print("-" * 60)
            for idx, channel in enumerate(channels, 1):
                print(f"{idx}. {channel['title'] or 'Sem título'}")
                print(f"   ID: {channel['id']}")
                if channel['username']:
                    print(f"   Username: @{channel['username']}")
                else:
                    print(f"   Username: Sem username (use o ID)")
                print(f"   Tipo: {'Canal de transmissão' if channel['is_broadcast'] else 'Grupo/Canal'}")
                if channel['is_verified']:
                    print(f"   ✓ Verificado")
                print()
        else:
            print("❌ Nenhum canal encontrado nos diálogos")
            print()
        
        # Mostrar grupos também (pode ser que o canal esteja como grupo)
        if groups:
            print("👥 GRUPOS E SUPERGRUPOS:")
            print("-" * 60)
            for idx, group in enumerate(groups, 1):
                print(f"{idx}. {group['title'] or 'Sem título'}")
                print(f"   ID: {group['id']}")
                if group['username']:
                    print(f"   Username: @{group['username']}")
                else:
                    print(f"   Username: Sem username (use o ID)")
                print(f"   Tipo: {group['type']}")
                print()
        
        # Tentar buscar o canal específico pelo nome
        print("=" * 60)
        print("🔎 Buscando 'Fly Drama Vídeos' especificamente...")
        print("=" * 60)
        
        search_terms = ["Fly Drama Vídeos", "flydramavideos", "flydramavídeos", "Fly Drama"]
        found_specific = False
        
        for term in search_terms:
            for chat in all_chats:
                title = (chat['title'] or '').lower()
                username = (chat['username'] or '').lower()
                if term.lower() in title or (chat['username'] and term.lower() in username):
                    print(f"\n✅ ENCONTRADO: {chat['title'] or 'Sem título'}")
                    print(f"   ID: {chat['id']}")
                    if chat['username']:
                        print(f"   Username: @{chat['username']}")
                    else:
                        print(f"   Username: Sem username")
                    print(f"   Tipo: {chat['type']}")
                    print(f"   Use no código: {chat['username'] if chat['username'] else chat['id']}")
                    found_specific = True
                    break
            if found_specific:
                break
        
        if not found_specific:
            print("\n⚠️  Canal 'Fly Drama Vídeos' não encontrado na lista acima.")
            print("   Possíveis causas:")
            print("   - O canal não está nos seus diálogos recentes")
            print("   - Você precisa acessar o canal pelo Telegram primeiro")
            print("   - O nome pode estar diferente")
            print("\n   💡 Tente:")
            print("   1. Abrir o canal no Telegram")
            print("   2. Enviar uma mensagem ou interagir com ele")
            print("   3. Executar este script novamente")
        
        print("\n" + "=" * 60)
        print("💡 Dica: Use o username (com @) ou o ID do canal no código")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro ao listar canais: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.stop()
        print("\n👋 Desconectado do Telegram")

if __name__ == "__main__":
    asyncio.run(list_channels())