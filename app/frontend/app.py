
import sys
import os
import json
from influxdb import InfluxDBClient
from flask import Flask, render_template


class Configuration:
    # load configuration from json file
    def __init__(self, file) -> None:
        self.file = file
        self.config = {}

    def load_config(self):
        if not os.path.isfile(self.file):
            print("ERROR: Configuration file does not exist")
            sys.exit(1)

        with open(self.file, 'r') as f:
            self.config = json.load(f)


class DbConnection:
    def __init__(self, host, port, username, password, ssl, timeout) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl
        self.timeout = timeout
        self.client = InfluxDBClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            ssl=self.ssl,
            timeout=self.timeout
        )

    def connect(self):
        try:
            self.client.ping()
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to InfluxDB: {e}")
            return False

    def write(self, data, database):
        try:
            self.client.write_points(data, database=database)
            return True
        except Exception as e:
            print(f"ERROR: Failed to write data to InfluxDB database: {e}")
            return False

    def get_job_uuids(self):
        try:
            query = 'SHOW TAG values WITH KEY = "job_uuid"'
            self.client.switch_database('afs_store')
            rs = self.client.query(query)
            ret = []
            for r in rs.get_points():
                ret.append(r['value'])

            return list(set(ret))
        except Exception as e:
            print(f"ERROR: Failed to write data to InfluxDB database: {e}")
            return False


app = Flask(__name__)


@app.after_request
def set_frame_options(response):
    response.headers['X-Frame-Options'] = 'allow-from *'
    return response


@app.route('/')
def index():

    db_config = Configuration('/opt/pafs/frontend/etc/db_cfg.json')
    db_config.load_config()
    db = DbConnection(
        db_config.config['host'],
        db_config.config['port'],
        db_config.config['username'],
        db_config.config['password'],
        db_config.config['ssl'],
        db_config.config['timeout']
    )
    db.connect()

    job_uuids = db.get_job_uuids()
    pafs_ip = os.environ.get("PAFS_IP", "127.0.0.1")
    return render_template('dashboard.html', job_uuids=job_uuids, pafs_ip=pafs_ip)


if __name__ == '__main__':
    app.run()
