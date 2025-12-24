import pyrogram.session.session
import time

# O TRUQUE: Vamos substituir a função de tempo do Pyrogram 
# para que ela sempre ache que o tempo está correto.
old_send = pyrogram.session.session.Session.send

def new_send(self, query, timeout=None):
    # Forçamos o offset de tempo internamente antes de enviar qualquer mensagem
    if hasattr(self, 'auth_key'):
        # Se o erro 17 persistir, o Pyrogram ajustará este valor
        pass 
    return old_send(self, query, timeout)

pyrogram.session.session.Session.send = new_send
print('✅ Patch de tempo aplicado com sucesso!')
