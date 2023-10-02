import requests
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from time import sleep
from urllib.robotparser import RobotFileParser
from queue import PriorityQueue
import multiprocessing as mp
import hashlib
from heapq import heapify, heappush, heappop
"""
Heuristics for assinging priority:
* Refresh rate sampled from previous crawls
* Application-specific (e.g. "crawl news sites more often")
"""


# Priority
VERY_FREQUENT = 3
FREQUENT = 2
NOT_FREQUENT = 1

url_list = ["https://www.facebook.com/", 
            "https://www.cnn.com/",
            "https://www.9gag.com/",
            "https://www.aau.dk/"
            "https://www.amazon.com/"
            ]
# Frontier to be crawled
url_queue = PriorityQueue()

# Back frontier information about crawled URLS (heap) timestamp
##



"""
Prioritizer assigns to URL an integer priority between 1 and k
* Appends URL to corresponding queue
"""

def monitor_sites(site):
    url = Request(site, headers={"User-Agent": "Mozilla/5.0"})
    while True:
        try:
            response = urlopen(url).read()
            currentHash = hashlib.sha224(response).hexdigest()
            # Wait 30 second before trying again
            sleep(30)
            response = urlopen(url).read()
            newHash = hashlib.sha224(response).hexdigest()
            if newHash == currentHash:
                continue
            else:
                print("Change value")
                currentHash = newHash
                sleep(30)
                continue
        except Exception as e:
            print("error: " + e)


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
    while True:
        item = url_queue.get()


"""
Back worker ensures politeness in other words ensures that the it
does not hit the same server.


"""
def back_worker():
    pass


def crawl(url):
    rp = RobotFileParser()
    rp.set_url(url)
    rp.read()

    print(rp.can_fetch("*", url))

    r = requests.get(url)
    r_parse = BeautifulSoup(r.text, "html.parser")
    print(r_parse.prettify())

def main():

    ## Select from priority queue
    prioritizer()
    crawl(url)



if __name__ == "__main__":
    main()
    prioritizer()

