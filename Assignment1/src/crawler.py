from time import time, sleep
import concurrent.futures
import threading
from extractor import Extractor
from database import Database, DB_Page_Types, DB_Data_Types
from utils import get_ip_from_URL, get_canonical_URL, get_hostname_from_URL

class Crawler:

    def __init__(self, frontier: list[str], worker_count: int = 1, default_access_period: float = 5.0) -> None:
        self.frontier: list[tuple[str, str]] = [(f, None) for f in frontier]
        self.extractors: list[Extractor] = [Extractor() for _ in range(worker_count)]
        self.worker_count: int = worker_count
        self.access_period: dict[str, float] = {}
        self.last_access_times: dict[str, float] = {}
        self.default_access_period: float = default_access_period
        self.master_lock = threading.RLock()
        self.terminate: bool = False
        self.db = Database(db_name = "mCubed", user = "mCubed", password = "crawling", host = "127.0.0.1", port = 5432)

    def run(self) -> None:
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.worker_count) as executor:
                for i in range(self.worker_count):
                    executor.submit(self._thread_worker, i)
            self.db.connection.close()
        except Exception as e:
            print(f'run threw {e}')

    def _thread_worker(self, id: int):
        try:
            with self.master_lock:
                cursor = self.db.connection.cursor()
                extractor = self.extractors[id]
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
                    print("sleeping...")
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
        except Exception as e:
            print(f'worker threw {e}')

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
            new_page = False
            if page_id == None:
                if extractor.content_hash != '':
                    page_id = self.db.get_page_by_hash(cursor, extractor.content_hash)
                if page_id == None:
                    page_type = DB_Page_Types.HTML
                    if extractor.content_type != None and extractor.content_type != 'text/html':
                        page_type = DB_Page_Types.BINARY
                    page_id = self.db.insert_page(
                        cursor, 
                        site_id, 
                        page_type, 
                        extractor.url, 
                        extractor.content, 
                        extractor.http_status, 
                        extractor.accessed_time, 
                        extractor.content_hash)
                    new_page = True
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

            if new_page:
                page_values = []
                for file in extractor.extracted_files:
                    data_type = None
                    '.pdf', '.doc', '.docx', '.ppt', '.pptx'
                    if file.endswith('.pdf'):
                        data_type = DB_Data_Types.PDF
                    elif file.endswith('.doc'):
                        data_type = DB_Data_Types.DOC
                    elif file.endswith('.docx'):
                        data_type = DB_Data_Types.DOCX
                    elif file.endswith('.ppt'):
                        data_type = DB_Data_Types.PPT
                    elif file.endswith('.pptx'):
                        data_type = DB_Data_Types.PPTX
                    page_values.append((page_id, data_type, None))
                if len(page_values) > 0:
                    self.db.insert_page_data_many(cursor, page_values)

                image_values = []
                for image in extractor.extracted_images:
                    typ = None
                    splits = image.split('.')
                    if len(splits) > 0:
                        typ = '.'+splits[-1]
                    image_values.append((page_id, image, typ, '', extractor.accessed_time))
                if len(image_values) > 0:
                    self.db.insert_image_many(cursor, image_values)


    