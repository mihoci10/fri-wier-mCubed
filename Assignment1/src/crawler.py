from time import time, sleep
import concurrent.futures
import threading
from extractor import Extractor

import socket
from urllib.parse import urlparse

class Crawler:

    def __init__(self, worker_count: int = 1, default_access_period: float = 5.0) -> None:
        self.frontier: list[str] = ['https://www.google.si', 'https://www.google.si', 'https://www.youtube.com', 'https://ucilnica.fri.uni-lj.si/']
        self.worker_count: int = worker_count
        self.access_period: dict[str, float] = {}
        self.last_access_times: dict[str, float] = {}
        self.default_access_period: float = default_access_period
        self.master_lock = threading.RLock()
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
                i = 0
                while (i < len(self.frontier)):
                    IP = self._get_ip_from_URL(self.frontier[i])
                    if self._can_access_IP(IP):
                        break
                    i += 1
                if (i != len(self.frontier)):
                    cur_link = self.frontier.pop(i)
            if (cur_link == None):
                sleep(1)
                continue

            print(f'Selected URL: {cur_link}')

            IP = self._get_ip_from_URL(cur_link)
            self._access_IP(IP)

            extractor.run(cur_link)

    def _can_access_IP(self, IP):
        with self.master_lock:
            if IP in self.last_access_times:
                cur_time = time()
                last_time = self.last_access_times[IP]

                period = self.default_access_period
                if IP in self.access_period:
                    period = self.access_period[IP]

                return (cur_time - last_time > period)
            
        return True
    
    def _access_IP(self, IP):
        with self.master_lock:
            self.last_access_times[IP] = time()

    def _get_ip_from_URL(self, URL):
        parsed = urlparse(URL)
        try:
            server_IP = socket.gethostbyname(parsed.hostname)
        except Exception as e:
            print(f'_get_ip_from_URL threw : {e}')
            server_IP = parsed.hostname
        return server_IP