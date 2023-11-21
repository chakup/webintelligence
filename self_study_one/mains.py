import requests
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from time import sleep
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlsplit
from http.client import InvalidURL
from queue import PriorityQueue
import multiprocessing as mp
import hashlib
from heapq import heapify, heappush, heappop
import itertools
from multiprocessing import Process
"""
Heuristics for assinging priority:
* Refresh rate sampled from previous crawls
* Application-specific (e.g. "crawl news sites more often")
"""






pq = []
entry_finder = {}
REMOVED = '<removed-taks>'
counter= itertools.count()


def add_task(task, priority=0):
    'Add a new task or update the priority of an existing task'
    if task in entry_finder:
        remove_task(task)
    count = next(counter)
    entry = [priority, count, task]
    entry_finder[task] = entry
    heappush(pq, entry)

def remove_task(task):
    'Mark an existing task as REMOVED.  Raise KeyError if not found.'
    entry = entry_finder.pop(task)
    entry[-1] = REMOVED

def pop_task():
    'Remove and return the lowest priority task. Raise KeyError if empty.'
    while pq:
        priority, count, task = heappop(pq)
        if task is not REMOVED:
            del entry_finder[task]
            return task
    raise KeyError('pop from an empty priority queue')




url_seeds = [
    
            "https://www.facebook.com", 
            "https://www.cnn.com",
            "https://www.9gag.com",
            "https://www.aau.dk",
            "https://www.amazon.com"

            ]



saved_title = []


# Frontier to be crawled
# frontier_queue = PriorityQueue()

# Back frontier information about crawled URLS (heap) timestamp
##

def prioritize_url(url):
    r = requests.head(url)
    # The more last_modified was made the more it should be prioritized
    last_modified_header = r.headers.get("Last-Modified")
    if last_modified_header: 
        ### Check other urls for their last-modified header
        ## If this is the only one put it in, the more it changes the more it shou
        print(last_modified_header)

    etag_header = r.headers.get("ETag")
    if etag_header:
        print(etag_header)

def prioritizer():
    prioritize_url("https://www.9gag.com/")


def add_to_frontier_queue(url: str):

    if url == "/" or url[0] == "#":
        print("Not a valid url seed. Excluding...")
    else:
        print(f"Adding {url} to frontier queue...")
        add_task(url)
        print(f"Added {url}")


"""
Front worker represents the front queues. It is used for prioritization
and ensures that the site is crawled. Priority is based on the frequency changes
in the site. THe seeds are given a scale from 1-3 to 3 based on how frequent their site changes.

First, high-quality pages that change frequently should be
prioritized for frequent crawling. Thus, the priority of a page should be a
function of both its change rate and its quality (using some reasonable quality
estimate).

"""
def front_worker():
    limit = 0
    for url in url_seeds:
        print(f"Adding {url} to frontier_queue")
        add_task(url) # We add task with the same priority: 0

    while (limit < 1000): # Stop when you have crawled approx. 1000 pages
        for url in pq:
            print("Crawling new !!!")
            # Check if it has been crawled before. Create a heap with a timestamp
            crawl(pop_task())
            limit += 1
            print("Counter is at ", limit)



"""
Back worker ensures politeness in other words ensures that the it
does not hit the same server.
"""

def back_worker():
    while(len(pq) != 0):
        r = requests.get(pop_task())
        print("_________________")
        print(r)
        print("_________________")
        r_parse = BeautifulSoup(r.text, "html.parser")
        title = r_parse.find("title")
        print(title)

## Discover new pages and crawl them
def crawl(url):
    try:
        print(f"Crawling {url}...")
        rp = RobotFileParser()
        rp.set_url(url)
        rp.read()
        print(rp.can_fetch("*", url))
        print(f"Sending GET request to {url}")
        r = requests.get(url)
        r_parse = BeautifulSoup(r.text, "html.parser")
        print("Looking for all links...")
        for a in r_parse.find_all('a', href=True):
            sleep(2)
            print("DEEEBUG", a["href"])
            retrieved_url = a["href"]
            add_to_frontier_queue(retrieved_url)
    except Exception as e:
        print("Skipping", e)


def main():

    p1 = Process(target=front_worker)
    p2 = Process(target=back_worker)
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    # front_worker()
    # back_worker()

    print("Done!")
if __name__ == "__main__":
    main()

