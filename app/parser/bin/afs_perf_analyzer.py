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


class dbConnection:
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


class nfsStat:
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
        lines = measurement['nfs.num_active_clients'].split('\n')
        line = [string for string in lines if re.search(pattern, string)]
        num_client_connected = line[0].split(':')[1].strip()
        return num_client_connected

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
            # res = {}
            # res['timestamp'] = m['timestamp']
            # res['num_active_clients'] = self.get_num_active_clients(m)
            self.num_active_clients_measurements.append(
                self.get_num_active_clients_measurement(m))


def main():
    parser = argparse.ArgumentParser(description='Analyze AFS performance')
    parser.add_argument(
        '-f', '--file', help='The file to analyze', required=True)
    args = parser.parse_args()

    db_config = Configuration('../etc/db_cfg.json')
    db_config.load_config()

    db = dbConnection(
        db_config.config['host'],
        db_config.config['port'],
        db_config.config['username'],
        db_config.config['password'],
        db_config.config['ssl'],
        db_config.config['timeout']
    )

    db.connect()

    job_uuid = uuid.uuid4()
    print(f"INFO: Job UUID: {job_uuid}")

    # I need to find files in a directory
    # and then parse them

    ns = nfsStat(job_uuid, "10.66.40.74")
    ns.parse_file(args.file)

    db.write(ns.num_active_clients_measurements, 'afs_store')


if __name__ == "__main__":
    main()
