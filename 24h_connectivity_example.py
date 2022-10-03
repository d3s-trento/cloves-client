"""
This script will use evb1000_connectivity test as a base and schedule it every hour for 24h
"""

from iot_testbed_client import Job, IoTTestbed
import json, copy
from datetime import datetime, timedelta

with open('examples/evb1000_connectivity_test.json', 'r') as fh:
    base = Job(json.load(fh))

errs, warns = base.validate()

for e in errs:
    print(f"Error: {e}")

for w in warns:
    print(f"Warning: {w}")

if len(errs) > 0:
    print("Unvalid base test, correct and retyr")
    exit(1)

hour0 = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
jobs = []
for i in range(24):
    job = copy.deepcopy(base)
    job.start_time = hour0 + timedelta(hours=i)
    print(job, job.start_time)
    errs, warns = job.validate()
    if len(errs) > 0:
        print("Errors: {errs}")
        exit(1)
    jobs.append(job)

with IoTTestbed() as iott:
    for j in jobs:
        iott.schedule(j)

print("All test submitted")
