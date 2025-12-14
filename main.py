import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram_client import TelegramClient
from video_downloader import VideoDownloader
from clear_session import clear_session

# Carregar variáveis de ambiente
load_dotenv()

# Obter CHANNEL_NAME do .env (pode ser ID numérico ou username com @)
channel_name = os.getenv("TELEGRAM_CHANNEL_NAME")
if not channel_name:
    print("❌ Erro: TELEGRAM_CHANNEL_NAME deve estar configurado no arquivo .env!")
    print("\nPara obter o ID ou username do canal:")
    print("1. Execute: docker-compose run --rm app python list_channels.py")
    print("2. Copie o ID ou username do canal desejado")
    print("3. Adicione TELEGRAM_CHANNEL_NAME no arquivo .env")
    exit(1)

# Converter para int se for um número, caso contrário manter como string
try:
    CHANNEL_NAME = int(channel_name)
except ValueError:
    CHANNEL_NAME = channel_name

async def main():
    print("=" * 60)
    print("📱 Telegram Video Downloader")
    print("=" * 60)
    
    # Obter credenciais do Telegram
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print("❌ Erro: TELEGRAM_API_ID e TELEGRAM_API_HASH devem estar configurados!")
        print("\nPara obter suas credenciais:")
        print("1. Acesse https://my.telegram.org/apps")
        print("2. Faça login com sua conta do Telegram")
        print("3. Crie um aplicativo e copie o API ID e API Hash")
        print("4. Configure as variáveis de ambiente no arquivo .env")
        return
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ Erro: TELEGRAM_API_ID deve ser um número!")
        return
    
    # Conectar ao Telegram
    client = TelegramClient(api_id, api_hash)
    
    try:
        await client.connect()
    except Exception as e:
        error_str = str(e).lower()
        # Verificar se é erro de sessão locked
        if "locked" in error_str or "database is locked" in error_str:
            print("\n⚠️  Sessão bloqueada detectada!")
            print("🧹 Limpando sessão automaticamente...")
            print("=" * 60)
            
            # Limpar a sessão
            clear_session(client.session_name)
            
            # Tentar reconectar após limpar a sessão
            print("\n🔄 Tentando conectar novamente...")
            try:
                await client.connect()
                print("✅ Reconectado com sucesso após limpar a sessão!")
            except Exception as retry_error:
                print(f"\n❌ Erro ao reconectar após limpar a sessão: {retry_error}")
                print("💡 Você precisará autenticar novamente na próxima execução.")
                return
        else:
            # Re-raise outros erros
            raise
    
    try:
        downloader = VideoDownloader(client.client, CHANNEL_NAME)
        
        while True:
            # Menu de opções
            print("\n" + "=" * 60)
            print("📋 Opções de Download")
            print("=" * 60)
            print("1. Baixar vídeos por data")
            print("2. Baixar todo o conteúdo do canal")
            print("0. Sair")
            print("=" * 60)
            
            try:
                choice = input("\nEscolha uma opção (0, 1 ou 2): ").strip()
            except KeyboardInterrupt:
                print("\n\n⚠️  Operação cancelada pelo usuário.")
                choice = "0"
            
            if choice == "0":
                break
            elif choice == "1":
                print("\n📅 Informe a data de início (formato: DD/MM/YYYY)")
                date_str = input("Data: ").strip()
                
                try:
                    start_date = datetime.strptime(date_str, "%d/%m/%Y")
                    
                    print("\n📅 Informe a data de fim (formato: DD/MM/YYYY) ou pressione Enter para usar hoje")
                    end_date_str = input("Data: ").strip()
                    
                    if end_date_str:
                        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
                    else:
                        end_date = datetime.now()
                    
                    # Validar se a data de fim não é menor que a data de início
                    if end_date < start_date:
                        print(f"❌ Erro: A data de fim ({end_date.strftime('%d/%m/%Y')}) não pode ser menor que a data de início ({start_date.strftime('%d/%m/%Y')})!")
                        continue
                    
                    # Buscar vídeos do período
                    print(f"\n🔍 Buscando vídeos de {start_date.date()} até {end_date.date()}...")
                    try:
                        video_messages, filtered_messages = await downloader.list_videos_by_date(start_date, end_date)
                    except Exception as e:
                        error_str = str(e).lower()
                        print(f"\n❌ Erro ao buscar vídeos: {e}")
                        
                        # Verificar se é erro de acesso ao canal
                        if "peer id invalid" in error_str or "chat not found" in error_str or "not found" in error_str or "invalid" in error_str:
                            print("\n💡 Possíveis soluções:")
                            print("   1. Verifique se você tem acesso ao canal")
                            print("   2. Execute: docker-compose run --rm app python list_channels.py")
                            print("   3. Verifique se o ID do canal está correto no .env")
                            print(f"      Canal configurado: {CHANNEL_NAME}")
                        else:
                            import traceback
                            traceback.print_exc()
                        continue
                    
                    if not video_messages:
                        print("❌ Nenhum vídeo encontrado no período especificado.")
                        continue
                    
                    print(f"\n📊 Encontrados {len(video_messages)} vídeos no período especificado")
                    
                    # Perguntar se quer baixar vídeo específico
                    print("\n" + "=" * 60)
                    print("Deseja baixar um vídeo específico?")
                    print("1. Sim")
                    print("2. Não (baixar todos)")
                    
                    while True:
                        try:
                            download_specific = input("Escolha (1 ou 2) [2]: ").strip()
                        except KeyboardInterrupt:
                            print("\n\n⚠️  Operação cancelada pelo usuário.")
                            download_specific = "2"
                            break
                        
                        if download_specific in ["1", "2", ""]:
                            # Se vazio, usar padrão "2" (Não)
                            if download_specific == "":
                                download_specific = "2"
                            break
                        else:
                            print("❌ Opção inválida! Por favor, escolha 1 ou 2.")
                    
                    if download_specific == "1":
                        # Loop para permitir baixar múltiplos vídeos
                        while True:
                            # Listar vídeos encontrados
                            print("\n" + "=" * 60)
                            print("📋 Vídeos encontrados:")
                            print("=" * 60)
                            
                            # Códigos ANSI para cores: \033[31m = vermelho, \033[0m = reset
                            RED = "\033[31m"
                            RESET = "\033[0m"
                            
                            for idx, video_msg in enumerate(video_messages, 1):
                                # Buscar descrição para exibir como título
                                description_result = await downloader.get_description_from_previous_message(filtered_messages, video_msg)
                                description = None
                                if description_result:
                                    description, _ = description_result
                                title = downloader.extract_video_title(description) if description else None
                                date_str = video_msg.date.strftime("%d/%m/%Y")
                                
                                # Formatar exibição: "Data: DD/MM/YYYY - TÍTULO"
                                if title:
                                    # Limitar título para exibição
                                    display_title = title[:60] + "..." if len(title) > 60 else title
                                    print(f"{RED}{idx}{RESET}. Data: {date_str} - {display_title}")
                                else:
                                    print(f"{RED}{idx}{RESET}. Data: {date_str} - Vídeo {video_msg.id}")
                            
                            print("=" * 60)
                            
                            # Solicitar escolha do vídeo
                            while True:
                                try:
                                    video_choice = input(f"\nEscolha o número do vídeo (1-{len(video_messages)}) ou 0 para voltar: ").strip()
                                except KeyboardInterrupt:
                                    print("\n\n⚠️  Operação cancelada pelo usuário.")
                                    break
                                
                                try:
                                    video_index = int(video_choice) - 1
                                    
                                    if video_index < 0:
                                        # Voltar ao menu principal
                                        break
                                    
                                    if video_index >= len(video_messages):
                                        print(f"❌ Opção inválida! Escolha um número entre 1 e {len(video_messages)} ou 0 para voltar.")
                                        continue
                                    
                                    # Opção válida, sair do loop
                                    break
                                    
                                except ValueError:
                                    print(f"❌ Erro: Número inválido! Escolha um número entre 1 e {len(video_messages)} ou 0 para voltar.")
                            
                            # Se o usuário cancelou (KeyboardInterrupt), sair do loop
                            try:
                                video_index
                            except NameError:
                                break
                            
                            if video_index < 0:
                                # Voltar ao menu principal
                                break
                            
                            # Baixar vídeo selecionado
                            selected_video = video_messages[video_index]
                            await downloader.download_single_video(selected_video, filtered_messages)
                            
                            # Perguntar se deseja baixar mais algum
                            print("\n" + "=" * 60)
                            print("Deseja baixar mais algum vídeo?")
                            print("1. Sim")
                            print("2. Não")
                            
                            while True:
                                try:
                                    download_more = input("Escolha (1 ou 2) [2]: ").strip()
                                except KeyboardInterrupt:
                                    print("\n\n⚠️  Operação cancelada pelo usuário.")
                                    download_more = "2"
                                    break
                                
                                if download_more in ["1", "2", ""]:
                                    # Se vazio, usar padrão "2" (Não)
                                    if download_more == "":
                                        download_more = "2"
                                    break
                                else:
                                    print("❌ Opção inválida! Por favor, escolha 1 ou 2.")
                            
                            if download_more != "1":
                                # Voltar ao menu principal
                                break
                                
                    else:
                        # Baixar todos os vídeos do período
                        await downloader.download_videos_by_date(start_date, end_date)
                        # Voltar ao menu principal após concluir
                        
                except ValueError as e:
                    # Verificar se é erro de parsing de data ou outro ValueError
                    error_msg = str(e)
                    if "time data" in error_msg.lower() or "does not match format" in error_msg.lower():
                        print("❌ Erro: Formato de data inválido! Use DD/MM/YYYY")
                    else:
                        print(f"❌ Erro: {e}")
                        import traceback
                        traceback.print_exc()
            elif choice == "2":
                await downloader.download_all_videos()
            else:
                print("❌ Opção inválida! Por favor, escolha 0, 1 ou 2.")
                continue
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
    finally:
        try:
            await client.disconnect()
        except:
            pass
        print("\n👋 Encerrando aplicação...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário.")

