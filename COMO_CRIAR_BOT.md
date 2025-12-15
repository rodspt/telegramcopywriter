# 🤖 Como Criar um Novo Bot no Telegram

## Passo a Passo Completo

### 1️⃣ Abrir o BotFather

1. Abra o Telegram (app móvel ou desktop)
2. Na barra de pesquisa, digite: `@BotFather`
3. Clique no bot oficial (verificado com ✓)
4. Clique em "Iniciar" ou "Start"

### 2️⃣ Criar um Novo Bot

1. Envie o comando: `/newbot`
2. O BotFather perguntará: **"Alright, a new bot. How are we going to call it? Please choose a name for your bot."**
3. Digite um nome para o bot (ex: "DramaFlix Bot" ou "Meu Bot de Vídeos")
4. O BotFather perguntará: **"Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot."**
5. Digite um username único que termine com `bot` (ex: `dramaflix_bot` ou `meubot_videos_bot`)
   - ⚠️ Se o username já existir, o BotFather pedirá outro

### 3️⃣ Obter o Token

Após criar o bot, o BotFather enviará uma mensagem como:

```
Done! Congratulations on your new bot. You will find it at t.me/seu_bot_username_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. Use this token to access the HTTP API:

1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

### 4️⃣ Copiar o Token

1. Copie o token completo (ex: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890`)
2. ⚠️ **IMPORTANTE**: Mantenha este token seguro! Não compartilhe com ninguém!

### 5️⃣ Configurar no Projeto

Adicione o token no arquivo `.env`:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

## 📋 Comandos Úteis do BotFather

- `/mybots` - Ver seus bots
- `/token` - Ver o token novamente (se você perdeu)
- `/setdescription` - Definir descrição do bot
- `/setabouttext` - Definir texto "Sobre"
- `/setuserpic` - Definir foto de perfil
- `/setcommands` - Definir comandos do bot
- `/deletebot` - Deletar um bot

## ⚙️ Configurações Adicionais Recomendadas

### Definir Descrição

1. Envie: `/setdescription`
2. Escolha seu bot
3. Digite uma descrição (ex: "Bot para gerenciar vídeos do DramaFlix")

### Definir Comandos

1. Envie: `/setcommands`
2. Escolha seu bot
3. Digite os comandos, um por linha:
   ```
   start - Iniciar o bot
   help - Ajuda
   ```

### Definir Foto

1. Envie: `/setuserpic`
2. Escolha seu bot
3. Envie uma foto

## 🔐 Segurança

- ⚠️ **NUNCA** compartilhe seu token publicamente
- ⚠️ **NUNCA** commite o token no Git (use `.env` e adicione ao `.gitignore`)
- ⚠️ Se o token for exposto, use `/revoke` no BotFather para gerar um novo

## ✅ Verificar se o Bot Funciona

1. Procure pelo bot no Telegram usando o username (ex: `@seu_bot_username_bot`)
2. Clique em "Iniciar" ou "Start"
3. O bot deve responder (se você configurou comandos)

## 🎯 Próximos Passos

Após criar o bot:

1. ✅ Adicione o token no `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=seu_token_aqui
   TELEGRAM_API_ID=seu_api_id
   TELEGRAM_API_HASH=seu_api_hash
   ```

2. ✅ Adicione o bot ao grupo/canal onde deseja usar

3. ✅ Torne o bot administrador (se necessário)

4. ✅ Configure o ID do canal no `.env`:
   ```env
   DRAMAFLEX_CHANNEL=-1003542270835
   ```

## 💡 Dicas

- Use nomes descritivos para o bot
- Escolha um username fácil de lembrar
- Mantenha o token seguro
- Teste o bot antes de usar em produção

