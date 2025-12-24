FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema e configurar timezone
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime \
    && echo "America/Sao_Paulo" > /etc/timezone

# Copiar requirements e instalar dependências Python
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/videos /app/sessions

CMD ["python", "main.py"]

