"""
Script para inicializar o bot no grupo (forçar interação)
Isso resolve o problema de PEER_ID_INVALID quando o bot é administrador mas ainda não interagiu
"""
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

async def init_bot_in_group():
    """Força o bot a interagir com o grupo enviando uma mensagem de teste"""
    print("=" * 60)
    print("🔧 Inicializando Bot no Grupo")
    print("=" * 60)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    dramaflix_channel = os.getenv("DRAMAFLEX_CHANNEL", "-1003542270835")
    
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
        "init_bot_session",
        bot_token=bot_token,
        api_id=api_id,
        api_hash=api_hash,
        workdir="sessions"
    )
    
    try:
        print("\n🔄 Conectando ao Telegram...")
        await bot_client.start()
        bot_info = await bot_client.get_me()
        print(f"✅ Bot conectado: @{bot_info.username}\n")
        
        # Tentar acessar o grupo
        print(f"🔍 Tentando acessar o grupo: {dramaflix_channel}")
        
        try:
            # Tentar como int primeiro
            try:
                channel_id = int(dramaflix_channel)
                chat = await bot_client.get_chat(channel_id)
            except ValueError:
                chat = await bot_client.get_chat(dramaflix_channel)
            
            print(f"✅ Grupo encontrado: {chat.title} (ID: {chat.id})")
            
            # Verificar se o bot está no grupo
            try:
                member = await bot_client.get_chat_member(chat.id, bot_info.id)
                status_name = member.status.name if hasattr(member.status, 'name') else str(member.status)
                print(f"📊 Status do bot: {status_name}")
                
                if status_name not in ['ADMINISTRATOR', 'OWNER', 'administrator', 'owner']:
                    print("⚠️  Bot não é administrador!")
                    print("   Torne o bot administrador primeiro")
                    return
                
            except Exception as perm_error:
                error_perm_str = str(perm_error).lower()
                if "user not found" in error_perm_str or "not a member" in error_perm_str:
                    print("❌ Bot não está no grupo!")
                    print(f"   Adicione o bot @{bot_info.username} ao grupo primeiro")
                    return
                else:
                    print(f"⚠️  Erro ao verificar permissões: {perm_error}")
            
            # Tentar enviar uma mensagem de teste para forçar a interação
            print("\n📤 Enviando mensagem de teste para inicializar o bot no grupo...")
            try:
                test_message = await bot_client.send_message(
                    chat_id=chat.id,
                    text="🤖 Bot inicializado! Agora posso republicar vídeos."
                )
                print(f"✅ Mensagem de teste enviada com sucesso!")
                print(f"   Mensagem ID: {test_message.id}")
                print(f"\n✅ Bot agora conhece o grupo e está pronto para usar!")
                print(f"   Você pode deletar a mensagem de teste se quiser")
                
            except Exception as send_error:
                error_send_str = str(send_error).lower()
                print(f"❌ Erro ao enviar mensagem de teste: {send_error}")
                
                if "peer_id_invalid" in error_send_str:
                    print("\n💡 SOLUÇÃO MANUAL:")
                    print("   1. No grupo DramaFlix, envie qualquer mensagem")
                    print("   2. OU mencione o bot: @DoramaVideos_bot")
                    print("   3. OU envie um comando para o bot no grupo")
                    print("   4. Depois tente republicar um vídeo")
                elif "forbidden" in error_send_str:
                    print("   O bot precisa ter permissão para enviar mensagens!")
                else:
                    print("   Verifique as permissões do bot no grupo")
                    
        except Exception as chat_error:
            error_str = str(chat_error).lower()
            if "peer_id_invalid" in error_str or "peer id invalid" in error_str:
                print(f"❌ Bot ainda não conhece o grupo (PEER_ID_INVALID)")
                print(f"\n💡 SOLUÇÃO MANUAL (faça isso AGORA):")
                print(f"   ")
                print(f"   📱 No Telegram (app móvel ou desktop):")
                print(f"   ")
                print(f"   1. Abra o grupo DramaFlix")
                print(f"   2. Digite e envie esta mensagem:")
                print(f"      @{bot_info.username} teste")
                print(f"   ")
                print(f"   OU simplesmente:")
                print(f"   1. Abra o grupo DramaFlix")
                print(f"   2. Envie qualquer mensagem (ex: 'teste')")
                print(f"   ")
                print(f"   ⚠️  IMPORTANTE: Isso precisa ser feito MANUALMENTE no Telegram")
                print(f"   O bot precisa 'ver' uma mensagem no grupo para conhecê-lo")
                print(f"   ")
                print(f"   Depois de enviar a mensagem:")
                print(f"   - Aguarde 5-10 segundos")
                print(f"   - Execute este script novamente")
                print(f"   - OU tente republicar um vídeo diretamente")
            else:
                print(f"❌ Erro: {chat_error}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot_client.stop()
        print("\n👋 Desconectado")

if __name__ == "__main__":
    asyncio.run(init_bot_in_group())

