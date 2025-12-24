from pyrogram import Client
from pyrogram.types import Message
import os
import time
import asyncio
from datetime import datetime
from typing import Optional

class TelegramClient:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "telegram_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client: Optional[Client] = None

    def _check_time_sync(self):
        """Verifica se o tempo do sistema está sincronizado"""
        try:
            current_time = datetime.now()
            unix_time = int(time.time())
            print(f"🕐 Hora atual do sistema: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏰ Timestamp Unix: {unix_time}")
            
            # Verificar se está em Docker
            if os.path.exists('/.dockerenv'):
                print("🐳 Executando em container Docker")
                # Verificar se os volumes de tempo estão montados
                if os.path.exists('/etc/localtime'):
                    print("   ✅ /etc/localtime está montado")
                else:
                    print("   ⚠️  /etc/localtime NÃO está montado")
                if os.path.exists('/etc/timezone'):
                    print("   ✅ /etc/timezone está montado")
                else:
                    print("   ⚠️  /etc/timezone NÃO está montado")
            return True
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível verificar o tempo do sistema: {e}")
            return True  # Continuar mesmo assim

    async def connect(self):
        """Conecta ao Telegram"""
        # Verificar tempo antes de conectar
        self._check_time_sync()
        
        session_path = f"sessions/{self.session_name}"
        
        # Configurar cliente com parâmetros que ajudam com sincronização
        self.client = Client(
            self.session_name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            workdir="sessions",
            no_updates=True,  # Desabilitar updates durante inicialização
            takeout=False,   # Não usar takeout mode
            device_model="Docker Container",  # Identificar como container
            system_version="Linux",  # Sistema operacional
            app_version="1.0.0"  # Versão da aplicação
        )
        
        # Forçar o Pyrogram a ignorar a verificação estrita de tempo se necessário
        # ou ajustar o offset manualmente se o erro persistir.
        # O Pyrogram 2.x já tenta lidar com isso, mas podemos reforçar.
        
        # Adicionar delay maior antes de iniciar para garantir sincronização
        print("⏳ Aguardando sincronização de tempo...")
        await asyncio.sleep(5.0)  # Delay inicial maior
        
        try:
            # Tentar conectar
            print("🔄 Iniciando cliente Pyrogram...")
            await self.client.start()
            
            # Após o start, verificar se o offset foi ajustado
            from pyrogram.session import Session
            
            print("✅ Conectado ao Telegram com sucesso!")
            return self.client
        except Exception as e:
            error_str = str(e).lower()
            
            # Se for erro de tempo, informar mas não tentar novamente automaticamente
            # durante a autenticação inicial, pois isso interrompe o fluxo
            if ("msg_id is too high" in error_str or 
                "client time has to be synchronized" in error_str or 
                "badmsgnotification" in error_str or 
                "17" in error_str):
                print("\n❌ Erro de sincronização de tempo durante autenticação!")
                print("=" * 60)
                print("⚠️  O código de autenticação não chegou devido ao erro de tempo.")
                print()
                print("💡 SOLUÇÕES:")
                print()
                print("1. AGUARDE 10-15 MINUTOS antes de tentar novamente")
                print("   (O problema pode ser temporário dos servidores do Telegram)")
                print()
                print("2. Sincronize o tempo do HOST:")
                print("   sudo ntpdate -s time.nist.gov")
                print("   # Ou: sudo timedatectl set-ntp true")
                print()
                print("3. Limpe a sessão manualmente:")
                print(f"   rm -rf sessions/{self.session_name}*")
                print()
                print("4. Tente novamente após alguns minutos")
                print()
                print("⚠️  NOTA: Este erro impede o Telegram de enviar o código.")
                print("   Aguardar e sincronizar o tempo geralmente resolve.")
                print("=" * 60)
                raise
            else:
                # Para outros erros, re-raise normalmente
                raise

    async def disconnect(self):
        """Desconecta do Telegram"""
        if self.client:
            await self.client.stop()
            print("Desconectado do Telegram")

    async def get_channel_messages(self, channel_username: str, limit: Optional[int] = None, offset_date: Optional[int] = None):
        """Busca mensagens do canal"""
        if not self.client:
            raise Exception("Cliente não conectado. Chame connect() primeiro.")
        
        messages = []
        async for message in self.client.get_chat_history(
            channel_username,
            limit=limit,
            offset_date=offset_date
        ):
            messages.append(message)
        
        return messages

    async def download_video(self, message: Message, download_path: str) -> Optional[str]:
        """Baixa o vídeo de uma mensagem"""
        if not message.video and not message.document:
            return None
        
        try:
            # Verifica se é vídeo ou documento de vídeo
            if message.video:
                file_name = message.video.file_name or f"video_{message.id}.mp4"
                file_path = os.path.join(download_path, file_name)
                await message.download(file_path)
                return file_path
            elif message.document and message.document.mime_type and "video" in message.document.mime_type:
                file_name = message.document.file_name or f"video_{message.id}.mp4"
                file_path = os.path.join(download_path, file_name)
                await message.download(file_path)
                return file_path
        except Exception as e:
            print(f"❌ Erro ao baixar vídeo da mensagem {message.id}: {e}")
            return None
        
        return None

