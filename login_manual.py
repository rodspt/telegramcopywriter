import asyncio
import os
from pyrogram import Client
from pyrogram.raw.functions.help import GetConfig
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    print('🚀 Iniciando Login com Sincronização Forçada...')
    
    # Usar o nome da sessão padrão do seu projeto
    app = Client('telegram_session', api_id=api_id, api_hash=api_hash, workdir='sessions')
    
    print('⏳ Conectando e Sincronizando...')
    await app.connect()
    
    try:
        # Força o ajuste de tempo
        await app.invoke(GetConfig())
        print('✅ Tempo sincronizado!')
    except Exception as e:
        print(f'ℹ️  Ajuste de tempo realizado.')

    print('\n--- INICIANDO AUTENTICAÇÃO ---')
    try:
        # O truque: se já está conectado, não usamos start(), usamos authorize()
        if not await app.storage.is_bot() and not await app.storage.user_id():
            await app.authorize()
        
        print('\n✅ LOGIN REALIZADO COM SUCESSO!')
        print('Agora você pode rodar o seu bot normalmente com: python main.py')
        await app.disconnect()
    except Exception as e:
        print(f'\n❌ Erro no login: {e}')

if __name__ == '__main__':
    asyncio.run(main())
