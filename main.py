import database
import multiprocessing as mp
import sys
from crawler import *

NUM_PROCESS = 4
CRAWL_COOL_DOWN = 3
DATABASE_NAME = "crawler.db"

class ParallelProcessManager():
    def __init__(self, num_processes, url_queue):
        # parallel process manager initialisation, url queue is probably a multiprocessing queue initialised in the main function
        # database passed down to WebCrawler class
        self.num_processes = num_processes
        self.url_queue = url_queue
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
            process = mp.Process(target=self.run_crawler_process)
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

    def run_crawler_process(self):
        # each process creates an instance of the WebCrawler class and crawls urls from the url queue
        while self.url_queue and self.urls_crawled < self.max_urls:
            url = self.url_queue.get()
            print(f"Process {mp.current_process().pid} is crawling {url}")
            web_crawler = Crawler(url)
            web_crawler.set_database_name(DATABASE_NAME)
            results = web_crawler.start_crawling()
            self.lock.acquire()
            self.urls_crawled += 1
            self.lock.release()
            if results is None:
                continue
            print(self.urls_crawled)
            self.add_urls_to_queue(results.url_list)


def main(urls):
    database.Database(DATABASE_NAME)
    
    # Create multiprocessing manager to handle parallel processes
    with mp.Manager() as manager:
        url_queue = manager.Queue()  # Create multiprocessing queue to store urls

        # Instantiate the ParallelProcessManager
        process_manager = ParallelProcessManager(num_processes=NUM_PROCESS, url_queue=url_queue)
        
        process_manager.add_urls_to_queue(urls)  # Add initial URLs to the queue
        process_manager.start_crawler_process()




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
