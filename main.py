import multiprocessing as mp
import sys

class ParallelProcessManager():
    def __init__(self, num_processes, url_queue, database):
        # parallel process manager initialisation, url queue is probably a multiprocessing queue initialised in the main function
        # database passed down to WebCrawler class
        self.num_processes = num_processes
        self.url_queue = url_queue
        self.database = database

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
        web_crawler = WebCrawler(self.url_queue, self.database)
        while self.url_queue:
            url = self.url_queue.get()
            web_crawler.crawl_url(url)


def main():
    # example num_processes = 4

    # get initial urls from database

    # create multiprocessing queue to store urls
    with mp.Manager() as manager:
        url_queue = manager.Queue()

        # for initial urls in url_queue, put into mp queue

if __name__ == "__main__":
    try:
        url = sys.argv[1]
    except IndexError:
        print("Please input an URL!")
    main(url) # TODO: Change this to read from a list of starting URLs