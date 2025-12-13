#!/bin/bash
# Script para copiar arquivos de configuração após o initdb
# Este script será executado após a inicialização do banco

if [ -f /etc/postgresql/postgresql.conf ] && [ -d "$PGDATA" ]; then
    cp /etc/postgresql/postgresql.conf "$PGDATA/postgresql.conf"
    chown postgres:postgres "$PGDATA/postgresql.conf"
fi

if [ -f /etc/postgresql/pg_hba.conf ] && [ -d "$PGDATA" ]; then
    cp /etc/postgresql/pg_hba.conf "$PGDATA/pg_hba.conf"
    chown postgres:postgres "$PGDATA/pg_hba.conf"
    # Recarregar configuração
    psql -U telegram_user -d telegram_videos -c "SELECT pg_reload_conf();" || true
fi

