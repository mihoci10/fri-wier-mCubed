from time import time, sleep
import concurrent.futures
import threading
from extractor import Extractor

class Crawler:

    def __init__(self, worker_count: int = 1, default_access_period: float = 5.0) -> None:
        self.frontier: list[str] = ['https://www.google.si', 'https://www.youtube.com', 'https://ucilnica.fri.uni-lj.si/']
        self.worker_count: int = worker_count
        self.access_times: dict[str, float] = {}
        self.default_access_period: float = default_access_period
        self.master_lock = threading.Lock()
        self.terminate: bool = False

    def run(self) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.worker_count) as executor:
            for _ in range(self.worker_count):
                executor.submit(self._thread_worker)

    def _thread_worker(self):
        extractor = Extractor()
        while True:
            if self.terminate:
                break
            cur_link = None
            with self.master_lock:
                if (len(self.frontier) > 0):
                    cur_link = self.frontier.pop(0)
            if (cur_link == None):
                sleep(1)
                continue

            print(f'Selected URL: {cur_link}')
            extractor.run(cur_link)
            extractor.extract_links_from_file('Assignment1\web-content.txt')

            