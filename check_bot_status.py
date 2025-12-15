"""
Script para verificar se o bot está ativo e funcionando
"""
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

async def check_bot_status():
    """Verifica o status do bot"""
    print("=" * 60)
    print("🤖 Verificando Status do Bot")
    print("=" * 60)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not bot_token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não está configurado!")
        print("   Configure no arquivo .env")
        return
    
    if not api_id or not api_hash:
        print("❌ Erro: TELEGRAM_API_ID e TELEGRAM_API_HASH são necessários!")
        print("   Configure no arquivo .env")
        return
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ Erro: TELEGRAM_API_ID deve ser um número!")
        return
    
    # Criar cliente bot
    bot_client = Client(
        "check_bot_status_session",
        bot_token=bot_token,
        api_id=api_id,
        api_hash=api_hash,
        workdir="sessions"
    )
    
    try:
        print("\n🔄 Conectando ao Telegram...")
        await bot_client.start()
        
        # Obter informações do bot
        bot_info = await bot_client.get_me()
        
        print("\n✅ Bot está ATIVO e funcionando!")
        print("=" * 60)
        print(f"📋 Informações do Bot:")
        print(f"   Nome: {bot_info.first_name}")
        if bot_info.last_name:
            print(f"   Sobrenome: {bot_info.last_name}")
        print(f"   Username: @{bot_info.username}")
        print(f"   ID: {bot_info.id}")
        print(f"   É bot: {'Sim' if bot_info.is_bot else 'Não'}")
        print(f"   Verificado: {'Sim' if bot_info.is_verified else 'Não'}")
        print(f"   Link: https://t.me/{bot_info.username}")
        print("=" * 60)
        
        # Verificar se o bot está em algum grupo/canal
        print("\n🔍 Verificando grupos/canais...")
        dramaflix_channel = os.getenv("DRAMAFLEX_CHANNEL", "-1003542270835")
        
        # Tentar diferentes formatos
        channel_attempts = []
        
        # Se for link de convite, pular (bots não podem usar CheckChatInvite)
        if not (dramaflix_channel.startswith("https://t.me/+") or dramaflix_channel.startswith("t.me/+")):
            # Se for ID numérico, tentar diretamente
            try:
                channel_id_int = int(dramaflix_channel)
                channel_attempts.append(channel_id_int)
                channel_attempts.append(str(channel_id_int))
            except ValueError:
                channel_attempts.append(dramaflix_channel)
        else:
            print("   ⚠️  Link de convite detectado - bots não podem verificar links de convite")
            print("   💡 Use o ID do grupo em vez do link de convite")
            print(f"   💡 Configure: DRAMAFLEX_CHANNEL=-1003542270835")
        
        chat = None
        for attempt in channel_attempts:
            try:
                chat = await bot_client.get_chat(attempt)
                break
            except Exception as e:
                error_str = str(e).lower()
                if "bot_method_invalid" in error_str:
                    continue  # Tentar próximo formato
                elif "peer_id_invalid" in error_str or "peer id invalid" in error_str:
                    print(f"\n⚠️  Bot ainda não conhece o grupo (PEER_ID_INVALID)")
                    print(f"   💡 Isso pode acontecer mesmo se o bot for administrador")
                    print(f"   💡 O bot precisa 'interagir' com o grupo primeiro")
                    print(f"\n   🔧 SOLUÇÃO:")
                    print(f"   1. No grupo DramaFlix, envie qualquer mensagem")
                    print(f"   2. OU mencione o bot: @DoramaVideos_bot")
                    print(f"   3. OU envie um comando para o bot no grupo")
                    print(f"   4. Depois execute este script novamente")
                    print(f"\n   💡 Alternativa: Tente republicar um vídeo")
                    print(f"      O código tentará enviar uma mensagem e isso fará o bot conhecer o grupo")
                    return
                elif "chat not found" in error_str:
                    print(f"\n❌ Grupo não encontrado!")
                    print(f"   💡 Verifique se o ID está correto: {dramaflix_channel}")
                    return
                continue
        
        if chat:
            print(f"\n✅ Bot conhece o grupo DramaFlix!")
            print(f"   Nome: {chat.title}")
            print(f"   ID: {chat.id}")
            print(f"   Tipo: {chat.type.name if hasattr(chat.type, 'name') else chat.type}")
            
            # Verificar se o bot está no grupo
            try:
                member = await bot_client.get_chat_member(chat.id, bot_info.id)
                status_name = member.status.name if hasattr(member.status, 'name') else str(member.status)
                print(f"\n📊 Status do bot no grupo:")
                print(f"   Status: {status_name}")
                
                if status_name in ['ADMINISTRATOR', 'OWNER', 'administrator', 'owner']:
                    print("   ✅ Bot é ADMINISTRADOR - pode enviar mensagens!")
                    print("   ✅ Tudo configurado corretamente!")
                elif status_name in ['MEMBER', 'member']:
                    print("   ⚠️  Bot é MEMBRO, mas NÃO é administrador")
                    print("   ⚠️  Para enviar vídeos, o bot precisa ser administrador!")
                    print("   💡 Torne o bot administrador nas configurações do grupo")
                else:
                    print(f"   ⚠️  Status: {status_name}")
                    
            except Exception as perm_error:
                error_perm_str = str(perm_error).lower()
                if "user not found" in error_perm_str or "not a member" in error_perm_str:
                    print(f"\n❌ Bot NÃO está no grupo!")
                    print(f"   💡 Adicione o bot @{bot_info.username} ao grupo DramaFlix")
                    print(f"   💡 Depois torne o bot administrador")
                else:
                    print(f"\n⚠️  Erro ao verificar permissões: {perm_error}")
        else:
            print(f"\n⚠️  Não foi possível verificar o grupo")
            print(f"   ID configurado: {dramaflix_channel}")
            print(f"   💡 Certifique-se de que o bot está no grupo")
        
        print("\n" + "=" * 60)
        print("💡 Para testar o bot:")
        print(f"   1. Abra o Telegram")
        print(f"   2. Procure por: @{bot_info.username}")
        print(f"   3. Clique em 'Iniciar' ou 'Start'")
        print(f"   4. O bot deve responder (se tiver comandos configurados)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro ao verificar status do bot: {e}")
        error_str = str(e).lower()
        
        if "unauthorized" in error_str or "invalid token" in error_str:
            print("   💡 O token do bot está inválido ou foi revogado")
            print("   💡 Gere um novo token com /token no @BotFather")
        elif "flood" in error_str:
            print("   💡 Muitas tentativas. Aguarde alguns minutos")
        else:
            import traceback
            traceback.print_exc()
    finally:
        await bot_client.stop()
        print("\n👋 Desconectado")

if __name__ == "__main__":
    asyncio.run(check_bot_status())

