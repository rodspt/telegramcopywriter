FROM postgres:16

ARG RESTORE_BD
ARG POSTGRES_DB
ENV POSTGRES_DB=${POSTGRES_DB}
ENV RESTORE_BD=${RESTORE_BD}

# Instala PostGIS
RUN apt-get update \
    && apt-get install postgresql-16-postgis-3 -y \
    && apt-get install postgis -y

# Copia o script de restauração
COPY ./restore_database.sh /docker-entrypoint-initdb.d/restore_database.sh
RUN sed -i 's/\r$//g' /docker-entrypoint-initdb.d/restore_database.sh
RUN chmod +x /docker-entrypoint-initdb.d/restore_database.sh

# Expõe a porta padrão do PostgreSQL
EXPOSE 5432