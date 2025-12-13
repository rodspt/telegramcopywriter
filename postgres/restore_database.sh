#!/usr/bin/env bash
echo "Restaurando o Banco de Dados"
#pg_restore -v -d telegram_videos  /docker-entrypoint-initdb.d/restore.bd > /tmp/log
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE telegram_videos TO postgres"
echo "Banco de Dados Restaurado com Sucesso"
