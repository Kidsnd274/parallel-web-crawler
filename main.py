import multiprocessing as mp
import sys
# from dbinit import initialize_database
from crawler import *


class ParallelProcessManager():
    def __init__(self, num_processes, url_queue, database):
        # parallel process manager initialisation, url queue is probably a multiprocessing queue initialised in the main function
        # database passed down to WebCrawler class
        self.num_processes = num_processes
        self.url_queue = url_queue
        self.database = database
        self.urls_crawled = 0
        self.max_urls = 1000
        self.lock = mp.Lock()

    def add_urls_to_queue(self, urls):
        for url in urls:
            self.url_queue.put(url)

    def start_crawler_process(self):
        # create processes to run in parallel
        processes = []
        for i in range(self.num_processes):
            process = mp.Process(targer=self.run_crawler_process)
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

    def run_crawler_process(self):
        # each process creates an instance of the WebCrawler class and crawls urls from the url queue
        while self.url_queue and self.urls_crawled < self.max_urls:
            url = self.url_queue.get()
            web_crawler = Crawler(url)
            results = web_crawler.start_crawling()
            self.lock.acquire()
            self.urls_crawled += 1
            self.lock.release()
            self.add_urls_to_queue(results.url_list)


def main(urls):
    # example num_processes = 4
    # initialise database
    initialize_database()

    # get initial urls from database

    # create multiprocessing queue to store urls
    with mp.Manager() as manager:
        url_queue = manager.Queue()

        # for initial urls in url_queue, put into mp queue


if __name__ == "__main__":
    import pathlib
    if len(sys.argv) > 1: # Check if an argument is supplied
        try:
            starting_file = pathlib.Path(sys.argv[1])
        except IndexError:
            print("Please input a file name")
    else:
        starting_file = pathlib.Path("starting_urls.txt")

    if starting_file.is_file():
        with starting_file.open() as f:
            urls = [line.strip() for line in f]

        main(urls)
    else:
        print("Please provide a file of starting URLs or save it as starting_urls.txt")
        exit(1)
