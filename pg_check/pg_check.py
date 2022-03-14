#!/usr/bin/env python3
import psycopg2
import os
import configparser


class PgCheck:
    """
    PgCheck
    This class that makes a connection to a local postgresql instance and carries out checks to determine if the
    database server is healthy or not for now only basic checks are supported but more will come next
    """

    def __init__(self):
        self.disabled = None
        self.is_slave = None
        self.is_master = None
        self.is_online = None
        self.hostname = None
        self.port = None
        self.user = None
        self.password = None
        self.port = None
        self.dbname = None
        self.use_ssl = None
        self.connection = None
        if self.is_enabled():
            self.read_config()
            self.connect()

    def is_enabled(self):
        print("node disable is: %s", self.disabled)
        return False if os.path.isfile("/tmp/node_disabled") else True

    def read_config(self):
        try:
            config = configparser.ConfigParser()
            config.read("pgcheck.ini")
            for section in config.sections():
                self.hostname = config[section].get('hostname', 'localhost')
                self.port = int(config[section].getint('port', 5432 ))
                self.user = config[section].get('user', 'postgres')
                self.password = config[section].get('password', os.environ.get('PGCHECK_PASSWORD'))
                self.dbname = config[section].get('dbname', 'postgres')
        except configparser.NoSectionError as noSectionError:
            print("Config section does not exist: %s ", noSectionError.section)
        except configparser.Error as ParseError:
            print(ParseError)

    def connect(self):
        try:
            self.connection = psycopg2.connect(dbname=self.dbname, user=self.user, host=self.hostname, port=self.port,
                                               password=self.password)
        except psycopg2.OperationalError as connErr:
            print("Could not connect %s", connErr)
            self.is_online = False
        except psycopg2.Error as dbErr:
            print("Could not connect %s", dbErr.pgerror)
        else:
            self.is_online = True

    def check_recovery_mode(self):

        with self.connection:
            result = None
            with self.connection.cursor() as curs:
                curs.callproc("pg_is_in_recovery")
                result = curs.fetchone()
        self.is_slave = result[0]
        self.is_master = not result[0]

    def reply(self):
        if self.is_enabled() is False:
            print("""
            HTTP/1.1 503 Service Unavailable\r\n
            Content-Type: text/plain\r\n
            Connection: close\r\n
            Content-Length: 51\r\n
            Postgresql Cluster Node is manually disabled remove /tmp/node_disabled file to enable
            """)
        if self.is_online is False:
            print("""
            HTTP/1.1 503 Service Unavailable\r\n
            Content-Type: text/plain\r\n
            Connection: close\r\n
            Content-Length: 51\r\n
            Postgresql Cluster Node is offline or connection was not successful
            """)
        if self.is_master:
            print("""
            HTTP/1.1 200 OK\r\n
            Content-Type: text/plain\r\n
            Connection: close\r\n
            Content-Length: 51\r\n
            Postgresql Cluster Node ready for service
            """)

        if self.is_slave:
            print("""
            HTTP/1.1 503 Service Unavailable\r\n
            Content-Type: text/plain\r\n
            Connection: close\r\n
            Content-Length: 51\r\n
            Postgresql Cluster Node read-only
            """)


def main():
    pgcheck = PgCheck()
    if pgcheck.is_online:
        pgcheck.check_recovery_mode()
    pgcheck.reply()


if __name__ == '__main__':
    main()