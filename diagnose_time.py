"""
Script de diagnóstico para problemas de sincronização de tempo
"""
import os
import time
from datetime import datetime

def diagnose():
    """Diagnostica problemas de sincronização de tempo"""
    print("=" * 60)
    print("🔍 Diagnóstico de Sincronização de Tempo")
    print("=" * 60)
    
    # Verificar se está em Docker
    in_docker = os.path.exists('/.dockerenv')
    
    if in_docker:
        print("🐳 Executando em container Docker")
    else:
        print("💻 Executando no sistema host")
    
    print()
    
    # Tempo atual
    current_time = datetime.now()
    unix_time = int(time.time())
    
    print(f"📅 Data/Hora: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Timestamp Unix: {unix_time}")
    print()
    
    # Verificar timezone
    try:
        tz = os.environ.get('TZ', 'Não configurado')
        print(f"🌍 Variável TZ: {tz}")
    except:
        pass
    
    # Verificar arquivos de tempo
    print("\n📁 Verificando arquivos de configuração de tempo:")
    
    if os.path.exists('/etc/localtime'):
        print("   ✅ /etc/localtime existe")
        try:
            # Tentar ler o link simbólico
            if os.path.islink('/etc/localtime'):
                link_target = os.readlink('/etc/localtime')
                print(f"      → Aponta para: {link_target}")
            else:
                print("      → É um arquivo (não um link simbólico)")
        except:
            pass
    else:
        print("   ❌ /etc/localtime NÃO existe")
    
    if os.path.exists('/etc/timezone'):
        print("   ✅ /etc/timezone existe")
        try:
            with open('/etc/timezone', 'r') as f:
                tz_content = f.read().strip()
                print(f"      → Conteúdo: {tz_content}")
        except:
            pass
    else:
        print("   ❌ /etc/timezone NÃO existe")
    
    print()
    
    # Verificar se os volumes estão montados (Docker)
    if in_docker:
        print("🔗 Verificando montagem de volumes:")
        
        # Verificar se /etc/localtime parece ser um volume montado
        # (geralmente volumes montados têm permissões diferentes)
        try:
            stat_info = os.stat('/etc/localtime')
            print(f"   /etc/localtime: tamanho={stat_info.st_size} bytes")
        except:
            print("   ⚠️  Não foi possível verificar /etc/localtime")
    
    print()
    print("=" * 60)
    print("💡 SOLUÇÕES RECOMENDADAS:")
    print("=" * 60)
    
    if in_docker:
        print("1. Sincronize o tempo do HOST (não do container):")
        print("   sudo ntpdate -s time.nist.gov")
        print("   # Ou: sudo timedatectl set-ntp true")
        print()
        print("2. Verifique se os volumes estão montados no docker-compose.yml:")
        print("   - /etc/localtime:/etc/localtime:ro")
        print("   - /etc/timezone:/etc/timezone:ro")
        print()
        print("3. Reinicie o container:")
        print("   docker-compose restart app")
        print()
        print("4. Se o problema persistir, reconstrua:")
        print("   docker-compose build app")
        print("   docker-compose up -d")
    else:
        print("1. Sincronize o tempo do sistema:")
        print("   sudo ntpdate -s time.nist.gov")
        print("   # Ou: sudo timedatectl set-ntp true")
        print()
        print("2. Verifique se o relógio do sistema está correto")
    
    print("=" * 60)

if __name__ == "__main__":
    diagnose()

