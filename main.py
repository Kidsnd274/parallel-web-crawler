import database
import multiprocessing as mp
import sys
from crawler import *

NUM_PROCESS = 4
MAX_URLS = 10000
DATABASE_NAME = "crawler.db"

class ParallelProcessManager():
    def __init__(self, num_processes, url_queue):
        # parallel process manager initialisation, url queue is probably a multiprocessing queue initialised in the main function
        # database passed down to WebCrawler class
        self.num_processes = num_processes
        self.url_queue = url_queue
        self.urls_crawled = mp.Value('i', 0)
        self.max_urls = MAX_URLS
        self.db_lock = mp.Lock()

    def add_urls_to_queue(self, urls):
        for url in urls:
            self.url_queue.put(url)

    def start_crawler_process(self):
        # create processes to run in parallel
        processes = []
        for i in range(self.num_processes):
            process = mp.Process(target=self.run_crawler_process, args=(DATABASE_NAME, self.db_lock))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()
            
        print(f"FINISHED CRAWLING!!!")
        print(f"URLs Crawled: {self.urls_crawled}")
        
        db = database.Database("test.db", None)
        print(db.fetch_all_keyword_count())

    def run_crawler_process(self, db_name, db_lock):
        # each process creates an instance of the WebCrawler class and crawls urls from the url queue
        while self.url_queue:
            with self.urls_crawled.get_lock():
                if not self.urls_crawled.value < self.max_urls:
                    break

            url = self.url_queue.get()
            print(f"Process {mp.current_process().pid} is crawling {url}")
            db = database.Database(db_name, db_lock) # Instantiate the db with the lock
            
            try:
                web_crawler = Crawler(url)
                web_crawler.set_database(db)
                results = web_crawler.start_crawling()
            except Exception as e:
                print(f"[WARNING] P {mp.current_process().pid} encounted an error when crawling {url}")
                print(e)
                results = None
            
            if results is None:
                print(f"[WARNING] P {mp.current_process().pid} received None when crawling {url}")
                continue

            with self.urls_crawled.get_lock():
                self.urls_crawled.value += 1
                print(f"[INFO] URLs Crawled: {self.urls_crawled.value}")
            
            self.add_urls_to_queue(results.url_list)


def main(urls):
    # Initialize database
    db = database.Database(DATABASE_NAME, None)
    db.initialize_database()
    db = None
    
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
