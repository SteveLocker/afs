#!/usr/bin/env python3
import uuid
import argparse
import subprocess
import datetime
import json
import sys

def smbPstat(inputfile, job_uuid):

    # Set job UUID
    #inputfile = sys.argv[1]
    #job_uuid = sys.argv[2]
    timestamp = ""

    # Initial Run to strip the out the required data
    with open(inputfile, 'r') as f, open('parseme.out', 'w') as out_file:
        for line in f:
            if "TIMESTAMP" in line or "SMB Counters for FSVM" in line or "Total Ops" in line or "Average Latency" in line or "Average IOPS" in line:
                out_file.write(line)

    # Loop through each line of input

    ret = []
    with open('parseme.out', 'r') as f:
        for line in f:
            measurement = {}
            # Check if the line contains a timestamp
            if "#TIMESTAMP" in line:
                # Extract timestamp from line
                time = int(line.split()[1])
                #print(time)
                timestamp = datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%dT%H:%M:%SZ')
                #print(timestamp)
            # Check if the line contains FSVM IP
            elif "FSVM" in line:
                # Extract FSVM IP from line
                fsvm_ip = line.split()[5]

            # Check if the line contains Average Latency
            elif "Average Latency" in line:
                # Extract Average Latency from line
                latency = float(line.split()[-1])

                # Create InfluxDB measurement for Average Latency
                measurement = {
                    "measurement": "smb_average_latency",
                    "tags": {"job_uuid": job_uuid, "fsvm_ip": fsvm_ip},
                    "time": timestamp,
                    "fields": {"value": latency}
                }

            # Check if the line contains Average IOPS
            elif "Average IOPS" in line:
                # Extract Average IOPS from line
                iops = float(line.split()[-1])

                # Create InfluxDB measurement for Average IOPS
                measurement = {
                    "measurement": "smb_average_iops",
                    "tags": {"job_uuid": job_uuid, "fsvm_ip": fsvm_ip},
                    "time": timestamp,
                    "fields": {"value": iops}
                }

            # Check if the line contains Total Ops
            elif "Total Ops" in line:
                # Extract Total Ops from line
                total_ops = int(line.split()[-1])

                # Create InfluxDB measurement for Total Ops
                measurement = {
                    "measurement": "smb_total_ops",
                    "tags": {"job_uuid": job_uuid, "fsvm_ip": fsvm_ip},
                    "time": timestamp,
                    "fields": {"value": total_ops}
                }

                #output_dict=create_dictionary()
                #output_dict=(measurement)
            if len(measurement) > 0:
                ret.append(measurement)

    # Remove temporary file
    subprocess.run(["rm", "parseme.out"])

    return ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze AFS performance')
    parser.add_argument(
        '-d', '--directory', help='.', required=True)
    parser.add_argument(
        '-f', '--file', help='The file to analyze', required=False)
    args = parser.parse_args()

    res = smbPstat("../perfout/smbStatPStats-041123-10:43:29.log", str(uuid.uuid4()))
    print(res)
