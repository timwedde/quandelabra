#!/usr/bin/env python3

### Warnings ###
import warnings
warnings.filterwarnings("ignore")

### System ###
import os
import io
import sys
import csv
import time
import asyncio
import argparse
import requests
from shutil import rmtree
from zipfile import ZipFile
from signal import signal, SIGINT, SIG_IGN
from aiohttp import ClientSession, TCPConnector

### Display ###
from tqdm import tqdm


DEFAULT_TASK_COUNT = 75
API_URL = "https://www.quandl.com/api/v3/datasets/{}/{}/data.csv?api_key={}"


class TaskPool(object):

    def __init__(self, workers, on_done):
        self._semaphore = asyncio.Semaphore(workers)
        self.on_done = on_done
        self._tasks = set()

    async def put(self, coro):
        await self._semaphore.acquire()
        task = asyncio.ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._on_task_done)

    def _on_task_done(self, task):
        self.on_done(task.result())
        self._tasks.remove(task)
        self._semaphore.release()

    async def join(self):
        await asyncio.gather(*self._tasks)

    async def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc, tb):
        return self.join()


def check(args):
    if os.path.exists(args.output_dir):
        print("The output directory exists. Do you want to overwrite it?")
        result = input("[y]es/[n]o: ").lower()
        if not result in ["y", "yes"]:
            print("Aborted")
            sys.exit(0)
        rmtree(args.output_dir)
    os.makedirs(args.output_dir, exist_ok=True)


async def fetch(url, ticker, session):
    async with session.get(url) as response:
        return (await response.read(), ticker)


def on_done(task_result):
    content, ticker = task_result
    with open(os.path.join(args.output_dir, "{}.csv".format(ticker)), "wb") as f:
        f.write(content)


async def main(args):
    if os.path.isfile("metadata.zip"):
        print("Last metadata download is out of date, clearing cache")
        second_since_last_download = time.time() - os.path.getmtime("metadata.zip")
        if second_since_last_download > 86400:
            os.remove("metadata.zip")

    if not os.path.isfile("metadata.zip"):
        print("Downloading metadata")
        ticker_list_url = "https://www.quandl.com/api/v3/databases/{}/metadata?api_key={}".format(args.dataset,
                                                                                                  args.api_key)
        response = requests.get(ticker_list_url, verify=False, stream=True)
        with open("metadata.zip", "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)

    with ZipFile("metadata.zip", "r") as zip_file:
        with zip_file.open(zip_file.namelist()[0]) as metadata_file:
            data = io.TextIOWrapper(metadata_file)
            reader = csv.reader(data)
            tickers = [line[0] for line in reader]

    print("Found {} tickers".format(len(tickers)))

    print("Starting downloads")
    connector = TCPConnector(limit=None)
    async with ClientSession(connector=connector) as session, TaskPool(args.num_tasks, on_done) as task_pool:
        for ticker in tqdm(tickers, total=len(tickers), unit="tickers"):
            await task_pool.put(fetch(API_URL.format(args.dataset, ticker, args.api_key), ticker, session))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="A tiny tool for quickly downloading large (and free) datasets from Quandl.")
    parser.add_argument("-d", "--dataset", type=str, dest="dataset", required=True,
                        metavar="quandl_code", help="(required) The Quandl Code for the dataset to download")
    parser.add_argument("-a", "--api_key", type=str, dest="api_key", required=True,
                        metavar="key", help="(required) Your Quandl API key")
    parser.add_argument("-o", "--output", type=str, dest="output_dir", required=True,
                        metavar="dir", help="(required) The directory to output data to")
    parser.add_argument("-t", "--tasks", type=int, dest="num_tasks", default=DEFAULT_TASK_COUNT,
                        metavar="N", help="The amount of tasks to spawn (default: {})".format(DEFAULT_TASK_COUNT))
    args = parser.parse_args()

    original_sigint_handler = signal(SIGINT, SIG_IGN)
    signal(SIGINT, original_sigint_handler)

    check(args)

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(args))
    except KeyboardInterrupt:
        print("\nReceived SIGINT, terminating...")

    print("Done.")
