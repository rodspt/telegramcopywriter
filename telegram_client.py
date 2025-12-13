from pyrogram import Client
from pyrogram.types import Message
import os
from typing import Optional

class TelegramClient:
    def __init__(self, api_id: int, api_hash: str, session_name: str = "telegram_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client: Optional[Client] = None

    async def connect(self):
        """Conecta ao Telegram"""
        session_path = f"sessions/{self.session_name}"
        self.client = Client(
            self.session_name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            workdir="sessions"
        )
        await self.client.start()
        print("✅ Conectado ao Telegram com sucesso!")
        return self.client

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

