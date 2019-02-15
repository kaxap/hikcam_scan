import os

import psycopg2.extras
from psycopg2 import IntegrityError

from app_logger import get_logger

logger = get_logger("database")
cursor = None
conn = None


def create_table_if_not_exists(tablename: str, create_query: str) -> bool:
    """
    creates a table if not exists
    :param tablename: name of the table
    :param create_query: create query to execute if table does not exist
    :return: True if table was created
    """

    if cursor:
        cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (tablename,))
        if not cursor.fetchone()[0]:
            cursor.execute(create_query)
            return True
        else:
            return False

    else:
        logger.error("Attempted to create a table while DB cursor has not been initialised")


def save_ip(ip: str, status: int):

    if cursor:
        try:
            cursor.execute("INSERT INTO ips (ip, status) VALUES (%s, %s)", (ip, status))
        except IntegrityError:
            cursor.execute("UPDATE ips SET status=%s WHERE ip=%s", (status, ip))


def init_database() -> bool:
    """
    initialises the database and populates global cursor and conn vars
    :return: True if it's a fresh start
    """
    global cursor
    global conn

    postgres_db = os.environ.get('POSTGRES_DB')
    postgres_user = os.environ.get('POSTGRES_USER')
    postgres_password = os.environ.get('POSTGRES_PASSWORD')
    postgres_host = os.environ.get('POSTGRES_HOST')
    postgres_port = os.environ.get('POSTGRES_PORT')

    connect_str = "dbname='{db}' user='{user}' password='{password}' host='{host}' port={port}".format(db=postgres_db,
                                                                                                       user=postgres_user,
                                                                                                       password=postgres_password,
                                                                                                       host=postgres_host,
                                                                                                       port=postgres_port)

    conn = psycopg2.connect(connect_str)
    conn.autocommit = True
    cursor = conn.cursor()

    """ create table vk_users """
    return create_table_if_not_exists('ips', 'CREATE TABLE ips (ip varchar(15) PRIMARY KEY, status int8); CREATE INDEX idx_ips ON ips USING btree(ip);')



