#!/bin/bash
# Script para atualizar o Pyrogram

echo "============================================================"
echo "🔄 Atualizando Pyrogram"
echo "============================================================"

# Verificar se está em Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Executando em container Docker"
    echo "   Execute: docker-compose exec app pip install --upgrade pyrogram"
else
    echo "💻 Executando no host"
    echo "   Atualizando Pyrogram..."
    pip install --upgrade pyrogram
    echo "✅ Pyrogram atualizado!"
fi

echo "============================================================"

