FROM postgres:9.6
COPY *.dict *.affix *.stop /usr/share/postgresql/9.6/tsearch_data/
COPY create_fts_dict.sql /docker-entrypoint-initdb.d/
COPY postgresql.conf ./

