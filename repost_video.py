"""
Módulo para republicar vídeos no canal DramaFlix usando autenticação de usuário (API_ID/API_HASH)
"""
import os
import asyncio
from pyrogram import Client
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

async def repost_to_dramaflix(video_path: str, description: Optional[str] = None, image_path: Optional[str] = None):
    """
    Republica um vídeo no canal DramaFlix usando autenticação de usuário (API_ID/API_HASH)
    
    Args:
        video_path: Caminho do arquivo de vídeo
        description: Descrição/título do vídeo (opcional)
        image_path: Caminho da imagem (opcional)
    
    Returns:
        True se publicado com sucesso, False caso contrário
    """
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    dramaflix_channel = os.getenv("DRAMAFLEX_CHANNEL", "DramaFlix")  # Nome, username (@DramaFlix) ou ID do canal
    
    if not api_id or not api_hash:
        print("❌ Erro: TELEGRAM_API_ID e TELEGRAM_API_HASH são necessários!")
        return False
    
    if not os.path.exists(video_path):
        print(f"❌ Erro: Arquivo de vídeo não encontrado: {video_path}")
        return False
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ Erro: TELEGRAM_API_ID deve ser um número!")
        return False
    
    # Criar cliente de usuário (não bot)
    user_client = Client(
        "dramaflix_user_session",
        api_id=api_id,
        api_hash=api_hash,
        workdir="sessions"
    )
    
    try:
        await user_client.start()
        user_info = await user_client.get_me()
        print(f"👤 Conectado como usuário: {user_info.first_name}")
        if user_info.username:
            print(f"   Username: @{user_info.username}")
        
        # Verificar se o canal existe - tentar diferentes formatos
        chat = None
        channel_attempts = []
        
        # Preparar diferentes formatos para tentar
        # Se for um número (ID), tentar diretamente e em diferentes formatos
        try:
            channel_id_int = int(dramaflix_channel)
            channel_attempts.append(channel_id_int)
            channel_attempts.append(str(channel_id_int))
        except ValueError:
            pass
        
        # Se não começa com @ ou -, tentar adicionar @
        if not dramaflix_channel.startswith("@") and not dramaflix_channel.startswith("-") and not dramaflix_channel.startswith("http"):
            channel_attempts.append(f"@{dramaflix_channel}")
        channel_attempts.append(dramaflix_channel)
        
        # Tentar cada formato
        last_error = None
        for attempt in channel_attempts:
            try:
                print(f"🔍 Tentando acessar com: {attempt} (tipo: {type(attempt).__name__})")
                chat = await user_client.get_chat(attempt)
                print(f"✅ Canal/Grupo encontrado: {chat.title or 'Sem título'} (ID: {chat.id})")
                print(f"   Tipo: {chat.type.name if hasattr(chat.type, 'name') else chat.type}")
                
                # Verificar se o usuário tem acesso
                try:
                    member = await user_client.get_chat_member(chat.id, user_info.id)
                    if hasattr(member, 'status'):
                        status_name = member.status.name if hasattr(member.status, 'name') else str(member.status)
                        print(f"   Status do usuário: {status_name}")
                        if status_name in ['ADMINISTRATOR', 'OWNER', 'CREATOR', 'administrator', 'owner', 'creator']:
                            print("   ✅ Usuário é administrador - pode enviar mensagens")
                        elif status_name in ['MEMBER', 'member']:
                            print("   ✅ Usuário é membro - pode enviar mensagens")
                        else:
                            print(f"   ℹ️  Status: {status_name}")
                    else:
                        print(f"   ℹ️  Status do usuário: {member.status}")
                except Exception as perm_error:
                    error_perm_str = str(perm_error).lower()
                    if "user not found" in error_perm_str or "not a member" in error_perm_str:
                        print(f"   ⚠️  Usuário não está no grupo/canal")
                        print(f"   💡 Adicione sua conta ao grupo DramaFlix primeiro")
                        last_error = f"Usuário não está no grupo. Adicione sua conta ao grupo DramaFlix."
                    else:
                        print(f"   ⚠️  Não foi possível verificar permissões: {perm_error}")
                
                break
            except Exception as e:
                error_str = str(e).lower()
                error_msg = str(e)
                last_error = error_msg
                
                # Mensagens mais específicas para diferentes erros
                if "chat not found" in error_str or "not found" in error_str:
                    print(f"⚠️  Tentativa com '{attempt}': Canal/Grupo não encontrado")
                    if isinstance(attempt, int) or (isinstance(attempt, str) and attempt.lstrip('-').isdigit()):
                        print("   💡 Verifique se o ID está correto e se você tem acesso ao grupo")
                elif "forbidden" in error_str or "no access" in error_str or "not a member" in error_str:
                    print(f"⚠️  Tentativa com '{attempt}': Sem acesso ao grupo/canal")
                    print("   💡 Adicione sua conta ao grupo primeiro")
                elif "peer_id_invalid" in error_str or "peer id invalid" in error_str:
                    print(f"⚠️  Tentativa com '{attempt}': Peer ID inválido ou desconhecido")
                    print("   💡 Verifique se você está no grupo e se o ID está correto")
                elif "username" not in error_str and "invalid" not in error_str:
                    print(f"⚠️  Tentativa com '{attempt}' falhou: {e}")
                continue
        
        # Se não encontrou, tentar buscar nos diálogos
        if not chat:
            print("⚠️  Não foi possível acessar o canal diretamente.")
            print("🔍 Tentando buscar nos diálogos...")
            try:
                async for dialog in user_client.get_dialogs():
                    dialog_title = (dialog.chat.title or "").lower()
                    dialog_username = (dialog.chat.username or "").lower()
                    channel_lower = dramaflix_channel.lower().replace("@", "")
                    
                    # Verificar se o título ou username corresponde
                    if (channel_lower in dialog_title or 
                        (dialog.chat.username and channel_lower in dialog_username) or
                        dialog_title == channel_lower):
                        chat = dialog.chat
                        print(f"✅ Canal encontrado nos diálogos: {chat.title or 'Sem título'} (ID: {chat.id})")
                        if chat.username:
                            print(f"   Username: @{chat.username}")
                        break
            except Exception as dialog_error:
                print(f"⚠️  Erro ao buscar diálogos: {dialog_error}")
        
        # Se ainda não encontrou, mostrar erro e instruções
        if not chat:
            print(f"\n❌ Erro: Não foi possível acessar o canal/grupo '{dramaflix_channel}'")
            if last_error:
                print(f"   Último erro: {last_error}")
            
            print("\n💡 SOLUÇÕES:")
            print("\n   📋 PASSO 1 - VERIFICAR ACESSO AO GRUPO:")
            print("      1. Certifique-se de que sua conta está no grupo DramaFlix")
            print("      2. Abra o grupo no Telegram e verifique se você tem acesso")
            print("      3. Se não estiver, use o link de convite: https://t.me/+uNSD258DeHJlY2Mx")
            print("\n   📋 PASSO 2 - VERIFICAR O ID CORRETO:")
            print("      ✅ ID confirmado pelo @getidsbot: -1003542270835 (SUPERGROUP)")
            print("      Configure no .env:")
            print("      DRAMAFLEX_CHANNEL=-1003542270835")
            print("\n   📋 PASSO 3 - TESTAR NOVAMENTE:")
            print("      Após verificar o acesso, tente republicar novamente")
            return False
        
        # Preparar caption (descrição)
        caption = description if description else None
        
        # Verificar novamente se o usuário pode enviar mensagens antes de tentar
        try:
            member = await user_client.get_chat_member(chat.id, user_info.id)
            status_name = member.status.name if hasattr(member.status, 'name') else str(member.status)
            print(f"   Verificando permissões... Status: {status_name}")
        except Exception as perm_check:
            print(f"⚠️  Não foi possível verificar permissões finais: {perm_check}")
            print("   Tentando enviar mesmo assim...")
        
        # Enviar vídeo
        print(f"📤 Enviando vídeo para {chat.title}...")
        print(f"   Arquivo: {os.path.basename(video_path)}")
        file_size_mb = os.path.getsize(video_path) / (1024*1024)
        print(f"   Tamanho: {file_size_mb:.2f} MB")
        
        # Se houver imagem, enviar primeiro a imagem com caption, depois o vídeo
        if image_path and os.path.exists(image_path):
            # Por enquanto, vamos enviar apenas o vídeo com caption
            pass
        
        # Enviar o vídeo com barra de progresso
        def progress_callback(current, total):
            if total > 0:
                percent = (current / total) * 100
                mb_current = current / (1024*1024)
                mb_total = total / (1024*1024)
                print(f"\r   📤 Enviando: {percent:.1f}% ({mb_current:.1f}MB / {mb_total:.1f}MB)", end="", flush=True)
        
        try:
            sent_message = await user_client.send_video(
                chat_id=chat.id,
                video=video_path,
                caption=caption,
                supports_streaming=True,
                progress=progress_callback
            )
            print()  # Nova linha após o progresso
        except Exception as send_error:
            error_send_str = str(send_error).lower()
            print(f"\n❌ Erro ao enviar vídeo: {send_error}")
            
            if "peer_id_invalid" in error_send_str or "peer id invalid" in error_send_str:
                print("\n💡 SOLUÇÃO: Você precisa estar no grupo primeiro!")
                print("   1. Abra o grupo DramaFlix no Telegram")
                print("   2. Certifique-se de que você tem acesso ao grupo")
                print("   3. Use o link de convite se necessário: https://t.me/+uNSD258DeHJlY2Mx")
                print("   4. Depois tente republicar novamente")
            elif "forbidden" in error_send_str or "not enough rights" in error_send_str:
                print("💡 Você precisa ter permissão para enviar mídia no grupo!")
                print("   Verifique se você é membro ou administrador do grupo")
            elif "file too large" in error_send_str:
                print("💡 O arquivo é muito grande. Telegram tem limite de 2GB.")
            elif "chat not found" in error_send_str:
                print("💡 Você não está no grupo. Adicione sua conta ao grupo primeiro!")
            else:
                print("💡 Verifique se você está no grupo e tem permissões para enviar mensagens")
            
            raise
        
        print(f"✅ Vídeo publicado com sucesso!")
        print(f"   Mensagem ID: {sent_message.id}")
        print(f"   Canal: {chat.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao republicar vídeo: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await user_client.stop()
