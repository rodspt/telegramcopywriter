import asyncio
import re
from datetime import datetime, timedelta, time
from typing import Optional, List, Union
from pyrogram.types import Message
from pyrogram import Client
from database import SessionLocal, Video, init_db
import os

class VideoDownloader:
    def __init__(self, client: Client, channel_name: Union[str, int], videos_path: str = "/app/videos"):
        self.client = client
        self.channel_name = channel_name
        self.videos_path = videos_path
        self.db = SessionLocal()
        
        # Criar diretório se não existir
        os.makedirs(videos_path, exist_ok=True)
        
        # Inicializar banco de dados
        init_db()

    def extract_video_title(self, description: Optional[str]) -> str:
        """Extrai o título do vídeo do texto que o precede"""
        if not description:
            return ""
        
        # Primeiro, procurar por texto em negrito (**texto**) no texto original
        bold_matches = re.findall(r'\*\*(.+?)\*\*', description)
        if bold_matches:
            # Pegar o primeiro texto em negrito (geralmente é o título)
            title = bold_matches[0].strip()
            if title:
                return title
        
        # Se não encontrar negrito, procurar pelo primeiro "|" e pegar o texto após ele
        if "|" in description:
            parts = description.split("|", 1)
            if len(parts) > 1:
                title = parts[1].strip()
                # Remover formatação markdown se houver
                title = re.sub(r'\*\*|\*|__|_', '', title).strip()
                # Pegar apenas a primeira linha
                title = title.split('\n')[0].strip()
                if title:
                    return title
        
        # Se não encontrar nada específico, pegar a primeira linha significativa
        lines = description.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:  # Ignorar linhas muito curtas
                # Remover formatação markdown
                title = re.sub(r'\*\*|\*|__|_|#', '', line).strip()
                if title:
                    return title[:100]  # Limitar a 100 caracteres
        
        # Se nada funcionar, retornar o início do texto (limitado, sem quebras de linha)
        text = " ".join(description.split())
        return text[:100]

    async def get_description_from_previous_message(self, all_messages: List[Message], video_message: Message) -> Optional[str]:
        """Busca descrição na mensagem anterior ao vídeo (considerando todas as mensagens)"""
        # Encontrar o índice do vídeo na lista completa de mensagens
        video_index = None
        for idx, msg in enumerate(all_messages):
            if msg.id == video_message.id:
                video_index = idx
                break
        
        if video_index is None:
            return None
        
        # As mensagens vêm em ordem decrescente (mais recentes primeiro)
        # Então video_index + 1 é a mensagem mais recente (anterior na ordem cronológica)
        # Mas na verdade, precisamos procurar mensagens que vieram ANTES do vídeo cronologicamente
        # Como a lista está em ordem decrescente, mensagens com índice MENOR são mais recentes
        # Então precisamos procurar mensagens com índice MAIOR (mais antigas na lista = mais antigas cronologicamente)
        
        # Buscar mensagens posteriores na lista (que são mais antigas cronologicamente)
        # Mas também verificar mensagens anteriores na lista (mais recentes) caso o título esteja depois
        for i in range(1, min(11, len(all_messages) - video_index)):
            # Procurar mensagens mais antigas (índice maior)
            next_index = video_index + i
            if next_index >= len(all_messages):
                break
                
            next_message = all_messages[next_index]
            
            # Verificar se é uma mensagem com texto (pode ter foto/imagem junto, mas precisa ter texto)
            # O texto pode estar em message.text ou message.caption (legenda de foto)
            message_text = next_message.text or (next_message.caption if hasattr(next_message, 'caption') else None)
            has_text = message_text and message_text.strip()
            
            # Não pode ser vídeo ou documento de vídeo
            is_not_video = (
                not next_message.video and 
                not (next_message.document and next_message.document.mime_type and "video" in next_message.document.mime_type)
            )
            
            if has_text and is_not_video:
                return message_text
        
        # Se não encontrou nas mensagens mais antigas, tentar nas mais recentes (índice menor)
        for i in range(1, min(6, video_index + 1)):
            prev_index = video_index - i
            if prev_index < 0:
                break
                
            prev_message = all_messages[prev_index]
            
            # Verificar se é uma mensagem com texto (pode ter foto/imagem junto, mas precisa ter texto)
            # O texto pode estar em message.text ou message.caption (legenda de foto)
            message_text = prev_message.text or (prev_message.caption if hasattr(prev_message, 'caption') else None)
            has_text = message_text and message_text.strip()
            
            # Não pode ser vídeo ou documento de vídeo
            is_not_video = (
                not prev_message.video and 
                not (prev_message.document and prev_message.document.mime_type and "video" in prev_message.document.mime_type)
            )
            
            if has_text and is_not_video:
                return message_text
        
        return None

    async def download_all_videos(self):
        """Baixa todos os vídeos do canal"""
        print(f"📥 Iniciando download de todos os vídeos do canal {self.channel_name}...")
        
        # Buscar todas as mensagens (não apenas vídeos) para encontrar descrições
        all_messages = []
        async for message in self.client.get_chat_history(self.channel_name):
            all_messages.append(message)
        video_messages = [msg for msg in all_messages if msg.video or (msg.document and msg.document.mime_type and "video" in msg.document.mime_type)]
        
        print(f"📊 Encontrados {len(video_messages)} vídeos para baixar de {len(all_messages)} mensagens totais")
        
        downloaded = 0
        skipped = 0
        
        for message in video_messages:
            # Verificar se já foi baixado
            existing = self.db.query(Video).filter(
                Video.message_id == message.id
            ).first()
            
            if existing and existing.is_downloaded:
                print(f"⏭️  Vídeo {message.id} já foi baixado anteriormente. Pulando...")
                skipped += 1
                continue
            
            # Buscar descrição na mensagem anterior (de todas as mensagens)
            description = await self.get_description_from_previous_message(all_messages, message)
            title = self.extract_video_title(description) or f"Vídeo {message.id}"
            
            # Baixar vídeo
            print(f"⬇️  Baixando: {title[:60]}{'...' if len(title) > 60 else ''}")
            file_path = await self._download_video(message, title)
            
            if file_path:
                # Salvar informações no banco
                video_info = message.video or message.document
                file_unique_id = video_info.file_unique_id if hasattr(video_info, 'file_unique_id') else str(message.id)
                
                video_record = Video(
                    message_id=message.id,
                    channel_name=str(self.channel_name),
                    file_name=os.path.basename(file_path),
                    file_path=file_path,
                    file_size=video_info.file_size if hasattr(video_info, 'file_size') else 0,
                    description=description,
                    message_date=message.date,
                    is_downloaded=True,
                    file_unique_id=file_unique_id
                )
                
                self.db.add(video_record)
                self.db.commit()
                
                print(f"✅ Vídeo {message.id} baixado com sucesso: {file_path}")
                downloaded += 1
            else:
                print(f"❌ Falha ao baixar vídeo {message.id}")
        
        print(f"\n📊 Resumo: {downloaded} vídeos baixados, {skipped} pulados")
        self.db.close()

    async def list_videos_by_date(self, start_date: datetime, end_date: Optional[datetime] = None) -> tuple[List[Message], List[Message]]:
        """Lista vídeos encontrados em um período específico (sem baixar)"""
        if end_date is None:
            end_date = datetime.now()
        
        # Converter datas para timestamp Unix para comparação
        start_timestamp = int(start_date.timestamp())
        
        # Ajustar end_date para o final do dia (23:59:59) para incluir todo o dia
        end_date_with_time = datetime.combine(end_date.date(), time(23, 59, 59))
        end_timestamp = int(end_date_with_time.timestamp())
        
        # Expandir o período de busca para incluir mensagens de texto anteriores aos vídeos
        # Buscar desde 1 dia antes do início do período para garantir que encontramos títulos
        search_start = start_date - timedelta(days=1)
        search_start_timestamp = int(search_start.timestamp())
        
        # Buscar todas as mensagens até a data de fim (incluindo 1 dia antes para títulos)
        # O Pyrogram get_chat_history com offset_date retorna mensagens até aquela data (em ordem decrescente)
        all_messages = []
        async for message in self.client.get_chat_history(self.channel_name, offset_date=end_date_with_time):
            msg_timestamp = int(message.date.timestamp())
            # Se a mensagem é anterior ao início da busca expandida, parar
            if msg_timestamp < search_start_timestamp:
                break
            # Se a mensagem está dentro do período expandido, adicionar
            if search_start_timestamp <= msg_timestamp <= end_timestamp:
                all_messages.append(message)
        
        # Filtrar mensagens no período e que são vídeos
        filtered_messages = []
        video_messages = []
        for msg in all_messages:
            msg_timestamp = int(msg.date.timestamp())
            # Incluir todas as mensagens no período expandido (para ter acesso aos títulos)
            # Mas marcar apenas vídeos dentro do período original
            if search_start_timestamp <= msg_timestamp <= end_timestamp:
                filtered_messages.append(msg)
                # Vídeos devem estar dentro do período original
                if start_timestamp <= msg_timestamp <= end_timestamp:
                    if msg.video or (msg.document and msg.document.mime_type and "video" in msg.document.mime_type):
                        video_messages.append(msg)
        
        return video_messages, filtered_messages

    async def download_videos_by_date(self, start_date: datetime, end_date: Optional[datetime] = None):
        """Baixa vídeos de um período específico"""
        if end_date is None:
            end_date = datetime.now()
        
        print(f"📥 Baixando vídeos do canal {self.channel_name} de {start_date.date()} até {end_date.date()}...")
        
        # Buscar vídeos do período
        video_messages, filtered_messages = await self.list_videos_by_date(start_date, end_date)
        
        print(f"📊 Encontrados {len(video_messages)} vídeos no período especificado de {len(filtered_messages)} mensagens totais")
        
        downloaded = 0
        skipped = 0
        
        for message in video_messages:
            # Verificar se já foi baixado
            existing = self.db.query(Video).filter(
                Video.message_id == message.id
            ).first()
            
            if existing and existing.is_downloaded:
                print(f"⏭️  Vídeo {message.id} já foi baixado anteriormente. Pulando...")
                skipped += 1
                continue
            
            # Buscar descrição na mensagem anterior (de todas as mensagens filtradas)
            description = await self.get_description_from_previous_message(filtered_messages, message)
            title = self.extract_video_title(description) or f"Vídeo {message.id}"
            
            # Baixar vídeo
            print(f"⬇️  Baixando: {title[:60]}{'...' if len(title) > 60 else ''}")
            file_path = await self._download_video(message, title)
            
            if file_path:
                # Salvar informações no banco
                video_info = message.video or message.document
                file_unique_id = video_info.file_unique_id if hasattr(video_info, 'file_unique_id') else str(message.id)
                
                video_record = Video(
                    message_id=message.id,
                    channel_name=str(self.channel_name),
                    file_name=os.path.basename(file_path),
                    file_path=file_path,
                    file_size=video_info.file_size if hasattr(video_info, 'file_size') else 0,
                    description=description,
                    message_date=message.date,
                    is_downloaded=True,
                    file_unique_id=file_unique_id
                )
                
                self.db.add(video_record)
                self.db.commit()
                
                print(f"✅ Vídeo {message.id} baixado com sucesso: {file_path}")
                downloaded += 1
            else:
                print(f"❌ Falha ao baixar vídeo {message.id}")
        
        print(f"\n📊 Resumo: {downloaded} vídeos baixados, {skipped} pulados")
        self.db.close()

    async def download_single_video(self, video_message: Message, all_messages: List[Message]):
        """Baixa um vídeo específico"""
        # Verificar se já foi baixado
        existing = self.db.query(Video).filter(
            Video.message_id == video_message.id
        ).first()
        
        if existing and existing.is_downloaded:
            print(f"⏭️  Vídeo {video_message.id} já foi baixado anteriormente.")
            return existing.file_path
        
        # Buscar descrição na mensagem anterior
        description = await self.get_description_from_previous_message(all_messages, video_message)
        title = self.extract_video_title(description) or f"Vídeo {video_message.id}"
        
        # Baixar vídeo
        print(f"⬇️  Baixando: {title[:60]}{'...' if len(title) > 60 else ''}")
        file_path = await self._download_video(video_message, title)
        
        if file_path:
            # Salvar informações no banco
            video_info = video_message.video or video_message.document
            file_unique_id = video_info.file_unique_id if hasattr(video_info, 'file_unique_id') else str(video_message.id)
            
            video_record = Video(
                message_id=video_message.id,
                channel_name=str(self.channel_name),
                file_name=os.path.basename(file_path),
                file_path=file_path,
                file_size=video_info.file_size if hasattr(video_info, 'file_size') else 0,
                description=description,
                message_date=video_message.date,
                is_downloaded=True,
                file_unique_id=file_unique_id
            )
            
            self.db.add(video_record)
            self.db.commit()
            
            print(f"✅ Vídeo {video_message.id} baixado com sucesso: {file_path}")
            self.db.close()
            return file_path
        else:
            print(f"❌ Falha ao baixar vídeo {video_message.id}")
            self.db.close()
            return None

    async def _download_video(self, message: Message, title: str = "") -> Optional[str]:
        """Baixa o vídeo de uma mensagem com progresso"""
        if not message.video and not message.document:
            return None
        
        # Obter extensão do arquivo original
        original_file_name = None
        if message.video:
            total_size = message.video.file_size or 0
            original_file_name = message.video.file_name or f"video_{message.id}.mp4"
        elif message.document:
            total_size = message.document.file_size or 0
            original_file_name = message.document.file_name or f"video_{message.id}.mp4"
        else:
            return None
        
        # Extrair extensão do arquivo original
        _, ext = os.path.splitext(original_file_name)
        if not ext:
            ext = ".mp4"  # Extensão padrão se não houver
        
        # Criar nome do arquivo baseado no título
        if title and title.strip():
            # Limpar título para usar como nome de arquivo (remover caracteres inválidos)
            # Remover caracteres inválidos para nome de arquivo
            safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
            # Remover espaços extras e substituir por underscore
            safe_title = re.sub(r'\s+', '_', safe_title.strip())
            # Limitar tamanho do nome (reservar espaço para extensão)
            max_length = 200 - len(ext)
            if len(safe_title) > max_length:
                safe_title = safe_title[:max_length]
            file_name = f"{safe_title}{ext}"
        else:
            # Se não houver título, usar nome original ou ID
            file_name = original_file_name if original_file_name != f"video_{message.id}.mp4" else f"video_{message.id}{ext}"
        
        file_path = os.path.join(self.videos_path, file_name)
        
        # Callback de progresso
        def progress_callback(current: int, total: int):
            if total > 0:
                percent = (current / total) * 100
                # Usar \r para sobrescrever a linha
                print(f"\r  Progresso: {percent:.1f}% ({current // 1024 // 1024}MB / {total // 1024 // 1024}MB)", end="", flush=True)
        
        try:
            # Verifica se é vídeo ou documento de vídeo
            if message.video:
                await message.download(file_path, progress=progress_callback)
                print()  # Nova linha após o progresso
                return file_path
            elif message.document and message.document.mime_type and "video" in message.document.mime_type:
                await message.download(file_path, progress=progress_callback)
                print()  # Nova linha após o progresso
                return file_path
        except Exception as e:
            print(f"\n❌ Erro ao baixar vídeo: {e}")
            return None
        
        return None
