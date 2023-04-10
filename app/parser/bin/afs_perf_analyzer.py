#!/usr/bin/env python

import sys
import os
import re
import argparse
import json
import uuid
import datetime
from influxdb import InfluxDBClient


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


class NfsStat:
    def __init__(self, job_uuid, fsvm_ip) -> None:
        self.job_uuid = job_uuid
        self.fsvm_ip = fsvm_ip
        self.raw_measurements = []
        self.num_active_clients_measurements = []

    def load_data(self, file):
        """Load data from file"""
        if not os.path.isfile(file):
            print("ERROR: File does not exist")
            sys.exit(1)

        print(f"INFO: Analyzing file: {file}")
        with open(file, 'r') as f:
            raw_data = f.read().split("#TIMESTAMP ")
            raw_data.pop(0)

        for d in raw_data:
            res = {}
            measurements = d.split("== -- ")
            timestamp = measurements.pop(0).strip()
            res['timestamp'] = timestamp
            for m in measurements:
                m_name = m.split('\n')[0].strip()
                res[m_name] = m

            self.raw_measurements.append(res)

        return True

    def get_num_active_clients(self, measurement):
        pattern = "Number of Clients connected:"
        res = measurement.get('nfs.num_active_clients')
        if res is not None:
            lines = res.split('\n')
            line = [string for string in lines if re.search(pattern, string)]
            num_client_connected = line[0].split(':')[1].strip()
            return int(num_client_connected)
        return -1

    def get_num_active_clients_measurement(self, raw_measurement):
        ret = self.get_num_active_clients(raw_measurement)
        mtime = datetime.datetime.fromtimestamp(
            int(raw_measurement['timestamp'].split(' : ')[0]))

        res = {}
        res['measurement'] = 'nfs_num_active_clients'
        res['tags'] = {
            'job_uuid': f"{self.job_uuid}",
            'fsvm_ip': f"{self.fsvm_ip}"
        }
        res['time'] = mtime.strftime('%Y-%m-%dT%H:%M:%SZ')
        res['fields'] = {'value': ret}
        return res

    def parse_file(self, file):
        self.load_data(file)
        for m in self.raw_measurements:
            self.num_active_clients_measurements.append(
                self.get_num_active_clients_measurement(m))


class Job():
    def __init__(self, path, db_connection):
        self.job_uuid = uuid.uuid4()
        self.path = path
        self.db_connection = db_connection

    def get_ip_from_file_name(self, filename):
        regex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        match = regex.search(filename)
        if match:
            return match.group()
        else:
            return None

    def find_files(self, pattern, path):
        result = []
        regex = re.compile(pattern)
        for root, dirs, files in os.walk(path):
            for file in files:
                if regex.match(file):
                    result.append(os.path.join(root, file))
        return result

    def parse_nfs_stat_files(self):
        files = self.find_files('nfsStat', self.path)
        for f in files:
            fsvm_ip = self.get_ip_from_file_name(f)
            print(f"INFO: Analyzing file: {f}")
            print(f"INFO: FSVM IP: {fsvm_ip}")
            nfs_stat = NfsStat(self.job_uuid, fsvm_ip)
            nfs_stat.parse_file(f)
            print(
                "INFO: Writing data to InfluxDB: nfs_num_active_clients measurements")
            self.db_connection.write(
                nfs_stat.num_active_clients_measurements, 'afs_store')


def main():
    parser = argparse.ArgumentParser(description='Analyze AFS performance')
    parser.add_argument(
        '-d', '--directory', help='Minerva performance bundle directory.', required=True)
    parser.add_argument(
        '-f', '--file', help='The file to analyze', required=False)
    args = parser.parse_args()

    db_config = Configuration('../etc/db_cfg.json')
    db_config.load_config()

    db_config = Configuration('../etc/db_cfg.json')
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

    jb = Job(args.directory, db)
    print(f"INFO: Job UUID: {jb.job_uuid}")

    jb.parse_nfs_stat_files()


if __name__ == "__main__":
    main()
