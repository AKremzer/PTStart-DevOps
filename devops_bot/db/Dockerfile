FROM postgres:15.0

ARG DB_REPL_USER
ARG DB_REPL_PASSWORD
ARG DB_PORT

COPY init.sql /docker-entrypoint-initdb.d/

RUN sed -i "s|\${DB_REPL_USER}|${DB_REPL_USER}|g" /docker-entrypoint-initdb.d/init.sql && \
    sed -i "s|\${DB_REPL_PASSWORD}|${DB_REPL_PASSWORD}|g" /docker-entrypoint-initdb.d/init.sql

EXPOSE $DB_PORT

