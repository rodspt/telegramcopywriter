"""
Script para verificar se as credenciais do Telegram estão configuradas corretamente
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def check_credentials():
    """Verifica se as credenciais estão configuradas"""
    print("=" * 60)
    print("🔍 Verificação de Credenciais do Telegram")
    print("=" * 60)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    channel_name = os.getenv("TELEGRAM_CHANNEL_NAME")
    
    print("\n📋 Status das Credenciais:")
    print("-" * 60)
    
    # Verificar Bot Token (prioridade)
    if bot_token:
        bot_token = bot_token.strip()
        if len(bot_token) >= 10:
            # Mostrar apenas parte do token por segurança
            masked_token = bot_token[:10] + "..." + bot_token[-5:] if len(bot_token) > 15 else bot_token[:10] + "..."
            print(f"✅ TELEGRAM_BOT_TOKEN: {masked_token} (configurado, {len(bot_token)} caracteres)")
            print("   🤖 Modo: Autenticação via Bot (recomendado)")
        else:
            print(f"❌ TELEGRAM_BOT_TOKEN: '{bot_token}' (INVÁLIDO - muito curto)")
    else:
        print("ℹ️  TELEGRAM_BOT_TOKEN: Não configurado (opcional)")
    
    # Verificar API ID
    if not api_id:
        print("ℹ️  TELEGRAM_API_ID: Não configurado (opcional se usar bot token)")
    else:
        api_id = api_id.strip()
        try:
            api_id_int = int(api_id)
            print(f"✅ TELEGRAM_API_ID: {api_id_int} (válido)")
        except ValueError:
            print(f"❌ TELEGRAM_API_ID: '{api_id}' (INVÁLIDO - deve ser um número)")
    
    # Verificar API Hash
    if not api_hash:
        print("ℹ️  TELEGRAM_API_HASH: Não configurado (opcional se usar bot token)")
    else:
        api_hash = api_hash.strip()
        if len(api_hash) >= 10:
            # Mostrar apenas parte do hash por segurança
            masked_hash = api_hash[:8] + "..." + api_hash[-4:] if len(api_hash) > 12 else api_hash[:8] + "..."
            print(f"✅ TELEGRAM_API_HASH: {masked_hash} (configurado, {len(api_hash)} caracteres)")
        else:
            print(f"❌ TELEGRAM_API_HASH: '{api_hash}' (INVÁLIDO - muito curto)")
    
    # Verificar Channel Name
    if not channel_name:
        print("❌ TELEGRAM_CHANNEL_NAME: NÃO CONFIGURADO")
    else:
        channel_name = channel_name.strip()
        print(f"✅ TELEGRAM_CHANNEL_NAME: {channel_name}")
    
    print("-" * 60)
    
    # Verificar se o arquivo .env existe
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"\n✅ Arquivo .env encontrado: {os.path.abspath(env_file)}")
    else:
        print(f"\n❌ Arquivo .env NÃO encontrado!")
        print(f"   Crie o arquivo .env na raiz do projeto: {os.path.abspath('.')}")
    
    # Resumo
    print("\n" + "=" * 60)
    has_valid_credentials = False
    
    if bot_token and len(bot_token.strip()) >= 10:
        print("✅ Bot Token configurado corretamente!")
        print("   🤖 Você pode usar autenticação via bot (mais simples)")
        has_valid_credentials = True
    elif api_id and api_hash:
        try:
            int(api_id.strip())
            if len(api_hash.strip()) >= 10:
                print("✅ Credenciais de usuário configuradas corretamente!")
                print("   👤 Você pode usar autenticação via API ID/API Hash")
                has_valid_credentials = True
            else:
                print("❌ API Hash parece inválido (muito curto)")
        except ValueError:
            print("❌ API ID inválido (deve ser um número)")
    else:
        print("❌ Credenciais não configuradas completamente")
        print("\n📝 Para configurar, escolha UMA opção:")
        print("\n   Opção 1 - Bot Token (RECOMENDADO):")
        print("   1. Abra o Telegram e procure por @BotFather")
        print("   2. Envie /newbot para criar um bot")
        print("   3. Copie o token do bot")
        print("   4. Adicione no arquivo .env:")
        print("      TELEGRAM_BOT_TOKEN=seu_bot_token")
        print("\n   Opção 2 - API ID/API Hash:")
        print("   1. Acesse https://my.telegram.org/apps")
        print("   2. Faça login e crie um aplicativo")
        print("   3. Copie o API ID e API Hash")
        print("   4. Adicione no arquivo .env:")
        print("      TELEGRAM_API_ID=seu_api_id")
        print("      TELEGRAM_API_HASH=seu_api_hash")
    
    if has_valid_credentials:
        print("\n💡 Para testar a conexão, execute:")
        print("   docker-compose run --rm app python list_channels.py")
    print("=" * 60)

if __name__ == "__main__":
    check_credentials()

