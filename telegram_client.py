from pyrogram import Client
from pyrogram.types import Message
import os
from typing import Optional

class TelegramClient:
    def __init__(self, bot_token: Optional[str] = None, api_id: Optional[int] = None, api_hash: Optional[str] = None, session_name: str = "telegram_session"):
        self.bot_token = bot_token
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client: Optional[Client] = None
        self.is_bot = bot_token is not None

    async def connect(self):
        """Conecta ao Telegram usando bot_token (se disponível) ou API_ID/API_HASH"""
        session_path = f"sessions/{self.session_name}"
        
        if self.bot_token:
            # Autenticação via bot token (não expira, mais simples)
            # IMPORTANTE: Pyrogram ainda precisa de api_id e api_hash para novas autorizações
            if self.api_id and self.api_hash:
                self.client = Client(
                    self.session_name,
                    bot_token=self.bot_token,
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    workdir="sessions"
                )
            else:
                # Tentar apenas com bot_token (pode funcionar se já houver sessão salva)
                self.client = Client(
                    self.session_name,
                    bot_token=self.bot_token,
                    workdir="sessions"
                )
            print("🤖 Conectando como bot...")
        elif self.api_id and self.api_hash:
            # Autenticação via API ID/API Hash (requer telefone e código)
            self.client = Client(
                self.session_name,
                api_id=self.api_id,
                api_hash=self.api_hash,
                workdir="sessions"
            )
            print("👤 Conectando como usuário...")
        else:
            raise ValueError("É necessário fornecer bot_token OU api_id e api_hash")
        
        try:
            await self.client.start()
            if self.is_bot:
                bot_info = await self.client.get_me()
                print(f"✅ Conectado ao Telegram como bot: @{bot_info.username}")
            else:
                print("✅ Conectado ao Telegram com sucesso!")
            return self.client
        except Exception as e:
            error_str = str(e).lower()
            error_msg = str(e)
            
            # Verificar se é erro de auth key not found
            is_auth_error = (
                "auth key not found" in error_str or
                "auth key" in error_str or
                "404" in error_msg or
                "transport error" in error_str or
                "server sent transport error" in error_str
            )
            
            if is_auth_error:
                # Re-lançar o erro para que seja tratado no main.py
                # O main.py vai limpar a sessão e tentar novamente
                raise Exception(f"Erro de autenticação: {error_msg}")
            else:
                # Re-lançar outros erros normalmente
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

