"""
Script para sincronizar o tempo do sistema antes de conectar ao Telegram
"""
import os
import time
import subprocess
from datetime import datetime

def sync_time():
    """Tenta sincronizar o tempo do sistema"""
    print("🕐 Verificando sincronização de tempo...")
    
    # Verificar se estamos em Docker
    if os.path.exists('/.dockerenv'):
        print("🐳 Executando em container Docker")
        print("   O tempo deve ser sincronizado através dos volumes montados do host")
        
        # Verificar se os arquivos de tempo estão montados
        if os.path.exists('/etc/localtime'):
            print("   ✅ /etc/localtime está montado")
        else:
            print("   ⚠️  /etc/localtime não está montado")
            
        if os.path.exists('/etc/timezone'):
            print("   ✅ /etc/timezone está montado")
        else:
            print("   ⚠️  /etc/timezone não está montado")
    else:
        print("💻 Executando no sistema host")
        # Tentar sincronizar usando ntpdate se disponível
        try:
            result = subprocess.run(
                ['which', 'ntpdate'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("   Tentando sincronizar com servidor NTP...")
                try:
                    subprocess.run(
                        ['sudo', 'ntpdate', '-s', 'time.nist.gov'],
                        check=True,
                        timeout=10
                    )
                    print("   ✅ Tempo sincronizado com sucesso")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    print("   ⚠️  Não foi possível sincronizar automaticamente")
        except:
            pass
    
    # Mostrar tempo atual
    current_time = datetime.now()
    print(f"   📅 Hora atual: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   ⏰ Timestamp Unix: {int(time.time())}")
    
    return True

if __name__ == "__main__":
    sync_time()

