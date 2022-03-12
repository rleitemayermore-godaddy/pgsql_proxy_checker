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
        self.hostname = None
        self.port = None
        self.user = None
        self.password = None
        self.port = None
        self.dbname = None
        self.use_ssl = None
        self.connection = None
        self.is_disabled()
        self.config_section = "pgcheck"

    def is_disabled(self):
        self.disabled = True if os.path.isfile("/tmp/node_disabled") else False
        print("node disable is: %s", self.disabled)

    def read_config(self):
        try:
            config = configparser.ConfigParser()
            config.read("pgcheck.ini")
            section = self.config_section
            if section in config.sections():
                self.hostname = config[section].get('hostname', 'localhost')
                self.port = int(config[section].getint('port', 5432 ))
                self.user = config[section].get('user', 'postgres')
                self.password = config[section].get('password', os.environ.get('PGCHECK_PASSWORD'))
                self.dbname = config[section].get('dbname', 'postgres')
        except configparser.Error as ParseError:
            print(ParseError)

    def connect(self):
        try:
            self.connection = psycopg2.connect(dbname=self.dbname, user=self.user, host=self.hostname, port=self.port,
                                               password=self.password)
        except psycopg2.OperationalError as connErr:
            print("Could not connect %s", connErr)
        except psycopg2.Error as dbErr:
            print("Could not connect %s", dbErr.pgerror)

    def check_recovery_mode(self):

        with self.connection:
            result = None
            with self.connection.cursor() as curs:
                curs.callproc("pg_is_in_recovery")
                result = curs.fetchone()
        self.is_slave = result[0]
        self.is_master = not result[0]

    def reply(self):
        if self.is_disabled():
            print("""
            HTTP/1.1 503 Service Unavailable\r\n
            Content-Type: text/plain\r\n
            Connection: close\r\n
            Content-Length: 51\r\n
            Postgresql Cluster Node is manually disabled remove /tmp/node_disabled file to enable
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