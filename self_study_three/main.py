import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.robotparser import RobotFileParser
from heapq import heapify, heappush, heappop
import itertools
from multiprocessing import Process, Manager
from multiprocessing.managers import SharedMemoryManager
from nltk.tokenize import word_tokenize
from nltk import PorterStemmer
import nltk
import math
from nltk.corpus import stopwords

nltk.download("punkt")
stop_words = set(stopwords.words("english"))

global corpus
global inverted_index
global total_docs

corpus = []
inverted_index = {}
total_docs = 0


def calculate_idf(term):
    # Calculate Document Frequency (dfdf):

    try:
        df = len(inverted_index[term])  # Document frequency
        print(f"Document frequency (df) of term {term} is:", df)
        td = total_docs  # Total documents
        # Calculate IDF:
        idf = math.log(td / df)
        print(f"The Inverse Document frequency (idf) of term {term} is:", idf)
        print(inverted_index)
        print(inverted_index[term])
    except KeyError:
        print(f"The term {term} is not in the index!")


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
        p2 += 1
    return result


def calculate_all_terms():
    for term in inverted_index:
        print(term)
        calculate_idf(term)


def preprocess_text(text):
    tokenized_text = word_tokenize(text)
    ps = PorterStemmer()
    # Exclude stop words and apply stemming
    filtered_tokens = [
        ps.stem(token) for token in tokenized_text if token.lower() not in stop_words
    ]
    return filtered_tokens


def add_doc(doc):
    # Tokenize doc into its own list
    global total_docs
    total_docs += 1
    tokenized_doc = word_tokenize(doc)
    ps = PorterStemmer()
    for t in tokenized_doc:
        # print(ps.stem(t))
        pass
    corpus.append(tokenized_doc)

    invert_index()
    print(inverted_index)
    calculate_all_terms()


def invert_index():
    for i, doc in enumerate(corpus):
        for term in doc:
            if term in inverted_index:
                inverted_index[term].add(i)
            else:
                inverted_index[term] = {i}


pq = []
entry_finder = {}
REMOVED = "<removed-taks>"
counter = itertools.count()


def add_task(task, priority=0):
    "Add a new task or update the priority of an existing task"
    if task in entry_finder:
        remove_task(task)
    count = next(counter)
    entry = [priority, count, task]
    entry_finder[task] = entry
    heappush(pq, entry)


def remove_task(task):
    "Mark an existing task as REMOVED.  Raise KeyError if not found."
    entry = entry_finder.pop(task)
    entry[-1] = REMOVED


def pop_task():
    "Remove and return the lowest priority task. Raise KeyError if empty."
    while pq:
        priority, count, task = heappop(pq)
        if task is not REMOVED:
            del entry_finder[task]
            return task
    raise KeyError("pop from an empty priority queue")


seed_urls = [
    # "https://www.facebook.com",
    "https://www.cnn.com",
    "https://www.9gag.com",
    "https://www.aau.dk",
    "https://www.amazon.com",
]


def crawl(seed_urls, max=1000):
    add_doc("Hello, Breaking news test")
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
                        soup = BeautifulSoup(r.text, "html.parser")
                        title = (
                            soup.find("title").string
                            if soup.find("title")
                            else "No title"
                        )
                        print(f"URL: {current_url}\nTitle: {title}\n")

                        ### Add title and link to corpus
                        add_doc(title)

                        for a in soup.find_all("a"):
                            sleep(2)
                            next_url = a["href"]
                            if next_url and next_url.startswith("http"):
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
    # with SharedMemoryManager() as smm:
    #     sl = smm.ShareableList(range(2000))
    # Divide the work among two processes, stori
    manager = Manager()
    term = manager.Value("term", True)

    ps = create_job(crawl, seed_urls)
    # ps.join()

    # while True:
    #     text = input("Select term to calculate IDF: ")
    #     term.value = text
    #     calculate_idf(term.value)


if __name__ == "__main__":
    main()
