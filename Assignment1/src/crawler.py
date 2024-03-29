from time import time, sleep
import concurrent.futures
import threading
from extractor import Extractor
from database import Database, DB_Page_Types, DB_Data_Types
from utils import get_ip_from_URL, get_canonical_URL, get_hostname_from_URL

class Crawler:

    def __init__(self, frontier: list[str], worker_count: int = 1, default_access_period: float = 5.0) -> None:
        self.frontier: list[tuple[str, str]] = [(f, None) for f in frontier]
        self.worker_count: int = worker_count
        self.access_period: dict[str, float] = {}
        self.last_access_times: dict[str, float] = {}
        self.default_access_period: float = default_access_period
        self.master_lock = threading.RLock()
        self.terminate: bool = False
        self.db = Database(db_name = "mCubed", user = "mCubed", password = "crawling", host = "127.0.0.1", port = 5432)

    def run(self) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.worker_count) as executor:
            for _ in range(self.worker_count):
                executor.submit(self._thread_worker)
        self.db.connection.close()

    def _thread_worker(self):
        with self.master_lock:
            cursor = self.db.connection.cursor()
        extractor = Extractor()
        while True:
            if self.terminate:
                break
            cur_link = None
            with self.master_lock:
                i = 0
                while (i < len(self.frontier)):
                    IP = get_ip_from_URL(self.frontier[i][0])
                    if self._can_access_IP(IP):
                        break
                    i += 1
                if (i != len(self.frontier)):
                    cur_link = self.frontier.pop(i)
            if (cur_link == None):
                sleep(1)
                continue

            print(f'Selected URL: {cur_link[0]}')
            URL = get_canonical_URL(cur_link[0])
            prev_URL = get_canonical_URL(cur_link[1])

            if self._check_page_exists(cursor, URL):
                self._insert_link(cursor, URL, prev_URL)
            else:
                IP = get_ip_from_URL(URL)
                self._access_IP(IP)

                extractor.run(URL)
                if extractor.permission:
                    self._insert_extractor_results(extractor, cursor, prev_URL)

                    for link in extractor.extracted_urls:
                        if get_hostname_from_URL(link).endswith('gov.si'):
                            with self.master_lock:
                                self.frontier.append((link, URL))

                if extractor.time_delay != None:
                    with self.master_lock:
                        self.access_period[IP] = extractor.time_delay
        cursor.close()

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

    def _check_page_exists(self, cursor, URL:str):
        with self.master_lock:
            page_id = self.db.get_page_by_url(cursor, URL)
            return page_id != None

    def _insert_link(self, cursor, cur_url:str, prev_url:str):
        with self.master_lock:
            page_id = self.db.get_page_by_url(cursor, cur_url)
            prev_page_id = self.db.get_page_by_url(cursor, prev_url)

            if page_id != None and prev_page_id != None:
                    self.db.insert_link(cursor, prev_page_id[0], page_id[0])

    def _insert_extractor_results(self, extractor: Extractor, cursor, src_site: str):
        with self.master_lock:
            site_id = self.db.get_site_name(cursor, extractor.domain)
            if site_id == None:
                robots = extractor.robots_content
                if robots == None:
                    robots = ''
                sitemap = extractor.sitemap_content
                if sitemap == None:
                    sitemap = ''
                site_id = self.db.insert_site(cursor, extractor.domain, robots, sitemap)
            else:
                site_id = site_id[0]

            page_id = self.db.get_page_by_url(cursor, extractor.url)
            orig_page_id = None
            if page_id == None:
                page_id = self.db.get_page_by_hash(cursor, extractor.content_hash)
                if page_id == None:
                    page_id = self.db.insert_page(
                        cursor, 
                        site_id, 
                        DB_Page_Types.HTML, 
                        extractor.url, 
                        extractor.content, 
                        extractor.http_status, 
                        extractor.accessed_time, 
                        extractor.content_hash)
                else:
                    orig_page_id = page_id[0]
                    page_id = self.db.insert_page(
                        cursor, 
                        site_id, 
                        DB_Page_Types.DUPLICATE, 
                        extractor.url, 
                        '', 
                        extractor.http_status, 
                        extractor.accessed_time, 
                        extractor.content_hash)
            else:
                page_id = page_id[0]

            if src_site != None:
                src_site_id = self.db.get_page_by_url(cursor, src_site)
                if src_site_id != None:
                    src_site_id = src_site_id[0]
                    self.db.insert_link(cursor, src_site_id, page_id)
                if orig_page_id != None:
                    self.db.insert_link(cursor, orig_page_id, page_id)


    