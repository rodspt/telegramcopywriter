# 📱 Telegram Video Downloader

Aplicação Docker para baixar vídeos de canais do Telegram, com armazenamento em volume Docker e banco de dados PostgreSQL para gerenciar metadados.

## 🚀 Funcionalidades

- ✅ Download de vídeos de canais do Telegram
- ✅ Opção de baixar todo o conteúdo ou filtrar por data
- ✅ Captura automática de descrições de mensagens anteriores aos vídeos
- ✅ Armazenamento persistente em volume Docker
- ✅ Banco de dados PostgreSQL para metadados
- ✅ Evita downloads duplicados

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Conta no Telegram
- API ID e API Hash do Telegram

## 🔧 Configuração

### 1. Obter credenciais do Telegram

1. Acesse [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. Faça login com sua conta do Telegram
3. Crie um aplicativo (se ainda não tiver)
4. Copie o **API ID** e **API Hash**

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
TELEGRAM_API_ID=seu_api_id_aqui
TELEGRAM_API_HASH=seu_api_hash_aqui
TELEGRAM_CHANNEL_NAME=ID_do_channel_id_ou_username
```

### 3. Obter o ID ou Username do Canal

Para descobrir o ID ou username do canal que você deseja baixar vídeos:

```bash
# Executar o script de listagem de canais
docker-compose run --rm app python list_channels.py
```

O script irá:
- Listar todos os canais que você faz parte
- Mostrar o **ID** e **Username** (se houver) de cada canal
- Exibir informações como: `ID: -1002402375685` ou `Username: @canal_exemplo`

**Copie o ID ou username** do canal desejado e adicione no arquivo `.env`:

- Se o canal tiver username: `TELEGRAM_CHANNEL_NAME=@canal_exemplo`
- Se o canal não tiver username: `TELEGRAM_CHANNEL_NAME=-1002402375685` (use o ID numérico)

### 4. Construir e executar

```bash
# Construir as imagens
docker-compose build

# Iniciar os serviços
docker-compose up -d postgres

# Aguardar o banco de dados estar pronto (alguns segundos)
# Depois executar a aplicação
docker-compose run --rm app
```

## 📖 Uso

Ao executar a aplicação, você verá um menu com as seguintes opções:

1. **Baixar vídeos por data**: Permite especificar um período para download do canal configurado
2. **Baixar todo o conteúdo**: Baixa todos os vídeos do canal configurado

### Primeira execução

Na primeira vez que executar, você precisará:
1. Informar seu número de telefone (com código do país, ex: +5511999999999)
2. Informar o código de verificação recebido no Telegram
3. Se tiver autenticação de dois fatores, informar a senha

A sessão será salva no diretório `sessions/` para não precisar autenticar novamente.

## 📁 Estrutura do Projeto

```
.
├── docker-compose.yml      # Configuração Docker Compose
├── Dockerfile              # Imagem Docker da aplicação
├── requirements.txt        # Dependências Python
├── main.py                 # Ponto de entrada da aplicação
├── telegram_client.py      # Cliente Telegram (Pyrogram)
├── video_downloader.py     # Lógica de download
├── database.py             # Modelos e configuração do banco
├── videos/                 # Volume Docker com vídeos baixados
└── sessions/               # Sessões do Telegram (autenticação)
```

## 🗄️ Banco de Dados

O PostgreSQL armazena as seguintes informações sobre cada vídeo:

- ID da mensagem
- Nome do canal
- Nome do arquivo
- Caminho completo do arquivo
- Tamanho do arquivo
- Descrição (se houver mensagem anterior)
- Data de download
- Data da mensagem original
- Status de download
- ID único do arquivo

## 🔍 Consultar vídeos baixados

Para consultar os vídeos salvos no banco de dados:

```bash
# Conectar ao banco de dados
docker-compose exec postgres psql -U telegram_user -d telegram_videos

# Consultar todos os vídeos
SELECT * FROM videos;

# Consultar vídeos por canal (use o ID ou nome do canal)
SELECT * FROM videos WHERE channel_name = '-1002402375685';

# Consultar vídeos baixados hoje
SELECT * FROM videos WHERE DATE(downloaded_at) = CURRENT_DATE;
```

## 📦 Volumes Docker

- `postgres_data`: Dados do PostgreSQL
- `videos_data`: Vídeos baixados (mapeado para `/app/videos` no container)

## 🛠️ Desenvolvimento

Para desenvolvimento local sem Docker:

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export TELEGRAM_API_ID=seu_api_id
export TELEGRAM_API_HASH=seu_api_hash
export DATABASE_URL=postgresql://telegram_user:telegram_pass@localhost:5432/telegram_videos

# Executar
python main.py
```

## ⚠️ Notas Importantes

- Os vídeos são salvos no volume Docker `videos_data`
- A sessão do Telegram é salva localmente em `sessions/`
- A aplicação evita baixar vídeos duplicados verificando o banco de dados
- Mensagens de texto anteriores aos vídeos são capturadas como descrição

## 📝 Licença

Este projeto é para uso pessoal.

