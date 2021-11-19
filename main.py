from scraper import get_jobs, query_processes, objs_to_csv
import time
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-q", help="Query file")
args = parser.parse_args()

query_file = args.q
output_dir = query_file.split('.')[0]

try:
    os.mkdir(output_dir)
except FileExistsError:
    print("Note: The folder already exists, the files is going to override. Press ^C to stop the execution")

with open(query_file, 'r') as f:
    queries = [line.split(',') for line in f.readlines()]

performance = []

for q in queries:
    time = query_processes(q[0].strip(), q[1].strip(), int(q[2]), output_dir)
    performance.append({
        'Q': q[0],
        'L': q[1],
        'Pages': q[2],
        'Time': time,
    })

objs_to_csv(performance, f'{output_dir}/performance.csv')