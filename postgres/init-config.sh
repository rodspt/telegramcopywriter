#!/bin/bash
set -e

# Este script roda ANTES do initdb, então precisamos criar o diretório se não existir
# e copiar os arquivos de configuração
if [ "$(id -u)" = '0' ]; then
    # Se estiver rodando como root, mudar para postgres
    exec su-exec postgres "$BASH_SOURCE" "$@"
fi

# Copiar arquivos de configuração para o diretório de dados do PostgreSQL
# O diretório será criado pelo initdb se não existir
if [ -f /tmp/postgresql.conf ] && [ -d "$PGDATA" ]; then
    cp /tmp/postgresql.conf "$PGDATA/postgresql.conf"
    chown postgres:postgres "$PGDATA/postgresql.conf"
fi

if [ -f /tmp/pg_hba.conf ] && [ -d "$PGDATA" ]; then
    cp /tmp/pg_hba.conf "$PGDATA/pg_hba.conf"
    chown postgres:postgres "$PGDATA/pg_hba.conf"
fi

echo "Configurações do PostgreSQL copiadas com sucesso!"

