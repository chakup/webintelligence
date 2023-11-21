import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.robotparser import RobotFileParser
from heapq import heapify, heappush, heappop
import itertools
from multiprocessing import Process
from nltk.tokenize import word_tokenize
from nltk import PorterStemmer




corpus = []
inverted_index = {}

## https://www.youtube.com/watch?v=o5uqBRt-akw
def and_postings(posting1, posting2):
    p1 = 0
    p2 = 0
    result = list()

    while p1 < len(posting1) and p2 < len(posting2):
        if posting1[p1] == posting2[p2]:
            result.append(posting1)
            p1 += 1
            p2 += 1
        elif posting1[p1] > posting2[p2]:
            p2 += 1
        else:
            p1 += 1
    return result


def or_postings(posting1, posting2):
    p1 = 0
    p2 = 0
    result = list()
    while p1 < len(posting1) and p2 < len(posting2):
        if posting1[p1] == posting2[p2]:
            result.append(posting1[p1])
            p1 += 1
            p2 += 1
        elif posting1[p1] > posting2[p2]:
            result.append(posting2[p2])
            p2 += 1
        else:
            result.append(posting1[p1])
            p1 += 1
    while p1 < len(posting1):
        result.append(posting1[p1])
        p1 += 1
    while p2 < len(posting2):
        result.append(posting2[p2])
        p2 +=1
    return result


def add_doc(doc):
    # Tokenize doc into its own list
    tokenized_doc = word_tokenize(doc)
    ps = PorterStemmer()
    for t in tokenized_doc:
        print(ps.stem(t))

    corpus.append(tokenized_doc)
    
    invert_index()





def getTopK(query):
    score = []


def invert_index():
    for i, doc in enumerate(corpus):
        for term in doc:
            if term in inverted_index:
                inverted_index[term].add(i)
            else: inverted_index[term] = {i}


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

seed_urls = [
            #"https://www.facebook.com", 
            "https://www.cnn.com",
            "https://www.9gag.com",
            "https://www.aau.dk",
            "https://www.amazon.com"
            ]

def crawl(seed_urls, max=1000):
    visited_urls = set()
    pages_crawled = 0

    for seed_url in seed_urls:
        rp = RobotFileParser()
        rp.set_url(seed_url)
        rp.read()

        if rp.can_fetch("*", seed_url):
            queue = [seed_url]

            while queue:
                current_url = queue.pop(0)
                if current_url not in visited_urls:
                    try:
                        r = requests.get(current_url)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        title = soup.find("title").string if soup.find("title") else "No title"
                        print(f"URL: {current_url}\nTitle: {title}\n")

                        ### Add title and link to corpus

                        add_doc(title)


                        for a in soup.find_all("a"):
                            sleep(2)
                            next_url = a["href"]
                            if next_url and next_url.startswith("http"):
                                #print(next_url)
                                queue.append(next_url)
                        visited_urls.add(current_url)
                        pages_crawled += 1

                        if pages_crawled >= max:
                            break
                    except Exception as e:
                        print(f"Error crawling {current_url}: {e}")
    print("Crawling completed")
                
                

def create_job(target, *args):
    p = Process(target=target, args=args)
    p.start()
    return p
def main():
    ps = create_job(crawl, seed_urls)
    ps.join()

if __name__ == "__main__":
    main()
