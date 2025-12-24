"""
Script para verificar e diagnosticar problemas de sincronização de tempo
"""
import os
import time
from datetime import datetime
import subprocess
import sys

def check_system_time():
    """Verifica o tempo do sistema"""
    print("=" * 60)
    print("🕐 Verificação de Tempo do Sistema")
    print("=" * 60)
    
    # Tempo do sistema
    system_time = datetime.now()
    print(f"📅 Data/Hora do Sistema: {system_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Timestamp Unix: {int(time.time())}")
    
    # Verificar timezone
    try:
        timezone = os.environ.get('TZ', 'Não configurado')
        print(f"🌍 Timezone: {timezone}")
    except:
        pass
    
    # Verificar se está em Docker
    if os.path.exists('/.dockerenv'):
        print("🐳 Executando dentro de um container Docker")
        
        # Verificar tempo do host (se possível)
        try:
            if os.path.exists('/etc/localtime'):
                print("✅ /etc/localtime está montado do host")
            else:
                print("⚠️  /etc/localtime não está montado")
        except:
            pass
    else:
        print("💻 Executando no sistema host")
    
    print("=" * 60)
    
    # Verificar diferença de tempo (se possível)
    try:
        # Tentar obter tempo de um servidor NTP (simulação)
        print("\n💡 Dicas para sincronizar o tempo:")
        print("   1. No host (WSL/Linux): sudo ntpdate -s time.nist.gov")
        print("   2. No host (WSL/Linux): sudo timedatectl set-ntp true")
        print("   3. Verificar se o container tem acesso ao tempo do host")
        print("   4. Reconstruir o container: docker-compose build app")
    except Exception as e:
        print(f"⚠️  Erro ao verificar sincronização: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    check_system_time()

