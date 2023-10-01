import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.robotparser import RobotFileParser

VERY_FREQUENT = 3
FREQUENT = 2
NOT_FREQUENT = 1

url_list = [
(NOT_FREQUENT,"https://www.facebook.com/"), 
(FREQUENT, "https://www.cnn.com/"), 
(VERY_FREQUENT, "https://www.9gag.com/"),
(NOT_FREQUENT, "https://www.aau.dk/")
]



"""
Front worker represents the front queues. It is used for prioritization
and ensures that the site is crawled. Anytime a site change then their
priority is one. This is set inside a heap.


"""
def front_worker():
    pass


"""
Back worker ensures politeness in other words ensures that the it
does not hit the same server.


"""
def back_worker():
    pass



def main():
    rp=RobotFileParser()
    rp.set_url(url_list[3][1])
    rp.read()

    print(rp.can_fetch("*", url_list[3][1]))

    r = requests.get(url_list[3][1])
    r_parse = BeautifulSoup(r.text, "html.parser")
    print(r_parse.prettify())



if __name__ == "__main__":
    main()

