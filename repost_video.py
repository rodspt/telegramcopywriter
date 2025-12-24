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
        workdir="sessions",
        no_updates=True,  # Desabilitar updates durante inicialização
        device_model="Docker Container",
        system_version="Linux",
        app_version="1.0.0"
    )
    
    try:
        # Adicionar delay maior antes de iniciar para garantir sincronização
        print("⏳ Aguardando sincronização de tempo...")
        await asyncio.sleep(5.0)  # Delay inicial maior
        
        # Tentar conectar - não interferir durante autenticação inicial
        try:
            await user_client.start()
            user_info = await user_client.get_me()
            print(f"👤 Conectado como usuário: {user_info.first_name}")
            if user_info.username:
                print(f"   Username: @{user_info.username}")
            
            print("✅ Conexão estabelecida com sucesso")
            print(f"🔍 Verificando variável DRAMAFLEX_CHANNEL: {dramaflix_channel}")
        except Exception as start_error:
            error_str = str(start_error).lower()
            # Verificar se é erro de sincronização de tempo
            if "msg_id is too high" in error_str or "client time has to be synchronized" in error_str or "badmsgnotification" in error_str or "17" in error_str:
                print("\n❌ Erro de sincronização de tempo detectado!")
                print("=" * 60)
                print("🔧 Solução automática: limpando sessão corrompida...")
                print("=" * 60)
                
                # Importar função de limpeza
                from clear_session import clear_session
                clear_session("dramaflix_user_session")
                
                print("\n✅ Sessão limpa com sucesso!")
                print("\n📋 IMPORTANTE - O código não chegou porque há erro de sincronização!")
                print("=" * 60)
                print("💡 SOLUÇÕES:")
                print()
                print("1. AGUARDE 10-15 MINUTOS antes de tentar novamente")
                print("   (O problema pode ser temporário dos servidores do Telegram)")
                print()
                print("2. Sincronize o tempo do HOST:")
                print("   sudo ntpdate -s time.nist.gov")
                print("   # Ou: sudo timedatectl set-ntp true")
                print()
                print("3. Verifique se o tempo está correto:")
                print("   date  # No host")
                print("   docker-compose exec app date  # No container")
                print()
                print("4. Tente novamente após alguns minutos:")
                print("   docker-compose run --rm app python main.py")
                print()
                print("⚠️  NOTA: Se o código não chegar, o problema é de sincronização")
                print("   de tempo que impede o Telegram de enviar o código.")
                print("   Aguardar e sincronizar o tempo geralmente resolve.")
                print("=" * 60)
                return False
            else:
                # Re-levantar exceção para ser capturada pelo except geral
                raise
        
        # Verificar se o canal existe - tentar diferentes formatos
        print(f"\n🔍 Procurando canal/grupo: {dramaflix_channel}")
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
                dialog_count = 0
                found_in_dialogs = False
                
                # Tentar buscar por ID primeiro
                try:
                    channel_id_int = int(dramaflix_channel)
                    async for dialog in user_client.get_dialogs():
                        dialog_count += 1
                        if dialog.chat.id == channel_id_int:
                            chat = dialog.chat
                            print(f"✅ Canal encontrado nos diálogos por ID: {chat.title or 'Sem título'} (ID: {chat.id})")
                            if chat.username:
                                print(f"   Username: @{chat.username}")
                            found_in_dialogs = True
                            break
                except (ValueError, Exception):
                    pass
                
                # Se não encontrou por ID, tentar buscar por nome
                if not found_in_dialogs:
                    channel_lower = dramaflix_channel.lower().replace("@", "").replace("-", "")
                    async for dialog in user_client.get_dialogs():
                        dialog_count += 1
                        dialog_title = (dialog.chat.title or "").lower()
                        dialog_username = (dialog.chat.username or "").lower()
                        
                        # Verificar se o título ou username corresponde
                        if (channel_lower in dialog_title or 
                            (dialog.chat.username and channel_lower in dialog_username) or
                            dialog_title == channel_lower or
                            "dramaflix" in dialog_title):
                            chat = dialog.chat
                            print(f"✅ Canal encontrado nos diálogos por nome: {chat.title or 'Sem título'} (ID: {chat.id})")
                            if chat.username:
                                print(f"   Username: @{chat.username}")
                            found_in_dialogs = True
                            break
                
                if not found_in_dialogs:
                    print(f"⚠️  Canal não encontrado nos {dialog_count} diálogos verificados")
                    print("   💡 Isso significa que você ainda não interagiu com o grupo")
                    
            except Exception as dialog_error:
                print(f"⚠️  Erro ao buscar diálogos: {dialog_error}")
                import traceback
                traceback.print_exc()
        
        # Se ainda não encontrou, tentar inicializar o grupo enviando uma mensagem de teste
        if not chat:
            print(f"\n❌ Erro: Não foi possível acessar o canal/grupo '{dramaflix_channel}'")
            if last_error:
                print(f"   Último erro: {last_error}")
            
            print("\n" + "=" * 60)
            print("🔧 TENTANDO SOLUÇÃO AUTOMÁTICA: Inicializando o grupo...")
            print("=" * 60)
            print("💡 O Telegram precisa 'conhecer' o grupo antes de permitir envio de mensagens.")
            print("   Vou tentar enviar uma mensagem de teste para inicializar o grupo...")
            
            try:
                # Tentar converter o ID para int
                channel_id_int = int(dramaflix_channel)
                
                # Tentar enviar uma mensagem de teste (silenciosa)
                print(f"📤 Tentando enviar mensagem de teste para inicializar o grupo (ID: {channel_id_int})...")
                try:
                    test_message = await user_client.send_message(
                        channel_id_int,
                        "🤖 Teste de inicialização - esta mensagem será deletada automaticamente"
                    )
                    print("✅ Mensagem de teste enviada com sucesso!")
                    print("   Isso inicializou o grupo para sua conta.")
                    
                    # Deletar a mensagem de teste após alguns segundos
                    print("   🗑️  Deletando mensagem de teste em 3 segundos...")
                    await asyncio.sleep(3)
                    try:
                        await user_client.delete_messages(channel_id_int, test_message.id)
                        print("   ✅ Mensagem de teste deletada")
                    except:
                        print("   ⚠️  Não foi possível deletar a mensagem (pode deletar manualmente)")
                    
                    # Agora tentar acessar o grupo novamente
                    print("\n🔄 Tentando acessar o grupo novamente...")
                    chat = await user_client.get_chat(channel_id_int)
                    print(f"✅ Grupo inicializado com sucesso: {chat.title or 'Sem título'} (ID: {chat.id})")
                    
                except Exception as send_test_error:
                    error_send_str = str(send_test_error).lower()
                    print(f"❌ Não foi possível enviar mensagem de teste: {send_test_error}")
                    
                    if "peer_id_invalid" in error_send_str or "peer id invalid" in error_send_str:
                        print("\n💡 O grupo ainda não foi inicializado.")
                        print("   Você precisa fazer isso MANUALMENTE:")
                    elif "forbidden" in error_send_str or "not enough rights" in error_send_str:
                        print("\n💡 Você não tem permissão para enviar mensagens no grupo.")
                        print("   Verifique suas permissões de administrador.")
                    else:
                        print("\n💡 Erro desconhecido ao tentar inicializar o grupo.")
                    
            except ValueError:
                print("⚠️  Não foi possível converter o ID do canal para número")
            except Exception as init_error:
                print(f"⚠️  Erro ao tentar inicializar o grupo: {init_error}")
            
            # Se ainda não encontrou após tentar inicializar
            if not chat:
                print("\n" + "=" * 60)
                print("💡 SOLUÇÕES MANUAIS:")
                print("=" * 60)
                print("\n   📋 PASSO 1 - INICIALIZAR O GRUPO MANUALMENTE:")
                print("      1. Abra o Telegram (app móvel ou desktop)")
                print("      2. Vá para o grupo DramaFlix")
                print("      3. Envie QUALQUER mensagem no grupo (ex: 'teste' ou 'oi')")
                print("      4. Aguarde 5-10 segundos")
                print("      5. Tente republicar o vídeo novamente")
                print("\n   📋 PASSO 2 - VERIFICAR ACESSO:")
                print("      - Certifique-se de que você está no grupo")
                print("      - Verifique se você tem permissão para enviar mensagens")
                print("      - Link de convite: https://t.me/+uNSD258DeHJlY2Mx")
                print("\n   📋 PASSO 3 - VERIFICAR O ID:")
                print("      ✅ ID configurado: -1003542270835 (SUPERGROUP)")
                print("      Se necessário, configure no .env:")
                print("      DRAMAFLEX_CHANNEL=-1003542270835")
                print("\n" + "=" * 60)
                return False
        
        print(f"\n✅ Canal encontrado com sucesso: {chat.title} (ID: {chat.id})")
        
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
        
        # Enviar vídeo primeiro (upload demorado)
        print(f"📤 Enviando vídeo para {chat.title}...")
        print(f"   Arquivo: {os.path.basename(video_path)}")
        file_size_mb = os.path.getsize(video_path) / (1024*1024)
        print(f"   Tamanho: {file_size_mb:.2f} MB")
        
        if image_path and os.path.exists(image_path):
            print(f"   📷 Foto será enviada após o vídeo ser carregado")
        
        # Enviar o vídeo com barra de progresso
        def progress_callback(current, total):
            if total > 0:
                percent = (current / total) * 100
                mb_current = current / (1024*1024)
                mb_total = total / (1024*1024)
                print(f"\r   📤 Enviando vídeo: {percent:.1f}% ({mb_current:.1f}MB / {mb_total:.1f}MB)", end="", flush=True)
        
        sent_video_message = None
        try:
            # Preparar parâmetros do vídeo
            video_params = {
                "chat_id": chat.id,
                "video": video_path,
                "supports_streaming": True,
                "progress": progress_callback
            }
            
            # Se houver imagem, usar como thumbnail do vídeo
            if image_path and os.path.exists(image_path):
                video_params["thumb"] = image_path
            
            # Não enviar caption no vídeo (será enviado na foto depois)
            # O vídeo será enviado sem descrição
            
            sent_video_message = await user_client.send_video(**video_params)
            print()  # Nova linha após o progresso
            print(f"✅ Vídeo publicado com sucesso! (ID: {sent_video_message.id})")
            
            # Agora que o vídeo foi enviado, enviar a foto separadamente
            # A foto será enviada depois, então aparecerá ANTES do vídeo visualmente
            if image_path and os.path.exists(image_path):
                print(f"\n📷 Enviando foto com descrição...")
                print(f"   Arquivo: {os.path.basename(image_path)}")
                try:
                    sent_photo = await user_client.send_photo(
                        chat_id=chat.id,
                        photo=image_path,
                        caption=caption
                    )
                    print(f"✅ Foto publicada com sucesso! (ID: {sent_photo.id})")
                    print(f"   📌 A foto aparecerá antes do vídeo no chat")
                except Exception as photo_error:
                    print(f"⚠️  Erro ao enviar foto: {photo_error}")
                    print("   O vídeo já foi publicado, mas a foto não pôde ser enviada")
        except Exception as send_error:
            error_send_str = str(send_error).lower()
            error_full = str(send_error)
            print(f"\n❌ Erro ao enviar vídeo: {error_full}")
            print("=" * 60)
            
            if "peer_id_invalid" in error_send_str or "peer id invalid" in error_send_str:
                print("\n💡 ERRO: Peer ID inválido")
                print("   Isso significa que o Telegram ainda não 'conhece' o grupo para sua conta.")
                print("\n   🔧 SOLUÇÃO:")
                print("   1. Abra o grupo DramaFlix no Telegram (app móvel ou desktop)")
                print("   2. Envie QUALQUER mensagem no grupo (ex: 'teste' ou 'oi')")
                print("   3. Aguarde 5-10 segundos")
                print("   4. Tente republicar novamente")
                print("\n   ⚠️  IMPORTANTE: Mesmo sendo admin, você precisa enviar uma mensagem")
                print("      no grupo primeiro para o Telegram registrar o grupo para sua conta.")
            elif "forbidden" in error_send_str or "not enough rights" in error_send_str:
                print("\n💡 ERRO: Sem permissão para enviar mídia")
                print("   Mesmo sendo admin, verifique:")
                print("   1. Se você tem permissão 'Post Messages' no grupo")
                print("   2. Se o grupo não está em modo 'Restrito'")
                print("   3. Se você não foi silenciado temporariamente")
            elif "file too large" in error_send_str:
                print("\n💡 ERRO: Arquivo muito grande")
                print("   O Telegram tem limite de 2GB por arquivo")
            elif "chat not found" in error_send_str:
                print("\n💡 ERRO: Grupo não encontrado")
                print("   1. Verifique se você está no grupo DramaFlix")
                print("   2. Verifique se o ID do grupo está correto no .env")
                print("   3. Tente usar o link de convite: https://t.me/+uNSD258DeHJlY2Mx")
            else:
                print("\n💡 ERRO DESCONHECIDO")
                print("   Detalhes completos do erro:")
                import traceback
                traceback.print_exc()
                print("\n   Verifique:")
                print("   1. Se você está no grupo e tem permissões para enviar mensagens")
                print("   2. Se o arquivo de vídeo existe e está acessível")
                print("   3. Se sua conexão com a internet está estável")
            
            print("=" * 60)
            raise
        
        # Verificar se o vídeo foi enviado com sucesso
        if sent_video_message:
            print(f"\n✅ Publicação concluída!")
            print(f"   Vídeo ID: {sent_video_message.id}")
            print(f"   Canal: {chat.title}")
            return True
        else:
            print(f"\n❌ Vídeo não foi enviado")
            return False
        
    except Exception as e:
        error_str = str(e).lower()
        error_msg = str(e)
        error_type = type(e).__name__
        
        print(f"\n❌ Erro ao republicar vídeo!")
        print(f"   Tipo: {error_type}")
        print(f"   Mensagem: {error_msg}")
        print("=" * 60)
        
        # Mostrar traceback completo para debug
        import traceback
        print("\n📋 Detalhes completos do erro:")
        traceback.print_exc()
        print("=" * 60)
        
        # Mensagens de erro mais específicas
        if "peer_id_invalid" in error_str or "peer id invalid" in error_str:
            print("\n💡 ERRO: Peer ID inválido")
            print("   Isso geralmente significa que:")
            print("   1. O usuário ainda não 'conhece' o grupo no Telegram")
            print("   2. Você precisa interagir com o grupo primeiro")
            print("\n   🔧 SOLUÇÃO:")
            print("   1. Abra o grupo DramaFlix no Telegram")
            print("   2. Envie qualquer mensagem no grupo (ex: 'teste')")
            print("   3. Aguarde 5-10 segundos")
            print("   4. Tente republicar novamente")
        elif "forbidden" in error_str or "not enough rights" in error_str:
            print("\n💡 ERRO: Sem permissão para enviar mensagens")
            print("   Mesmo sendo admin, verifique:")
            print("   1. Se você tem permissão para 'Post Messages' no grupo")
            print("   2. Se o grupo não está em modo 'Restrito'")
            print("   3. Se você não foi silenciado/banido temporariamente")
        elif "chat not found" in error_str:
            print("\n💡 ERRO: Grupo não encontrado")
            print("   1. Verifique se você está no grupo DramaFlix")
            print("   2. Verifique se o ID do grupo está correto no .env")
            print("   3. Tente usar o link de convite: https://t.me/+uNSD258DeHJlY2Mx")
        elif "file too large" in error_str:
            print("\n💡 ERRO: Arquivo muito grande")
            print("   O Telegram tem limite de 2GB por arquivo")
        elif "timeout" in error_str or "connection" in error_str:
            print("\n💡 ERRO: Problema de conexão")
            print("   1. Verifique sua conexão com a internet")
            print("   2. Tente novamente em alguns instantes")
        else:
            print("\n💡 Detalhes do erro:")
            import traceback
            traceback.print_exc()
        
        print("=" * 60)
        return False
    finally:
        try:
            await user_client.stop()
        except:
            pass
