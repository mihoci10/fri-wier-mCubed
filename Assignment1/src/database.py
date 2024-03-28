from datetime import datetime
import psycopg2
from psycopg2 import OperationalError
from enum import Enum

class DB_Page_Types(str, Enum):
    HTML = "HTML",
    BINARY = "BINARY",
    DUPLICATE = "DUPLICATE"
    FRONTIER = "FRONTIER"

class DB_Data_Types(str, Enum):
    PDF = "PDF",
    DOC = "DOC",
    DOCX = "DOCX",
    PPT = "PPT",
    PPTX = "PPTX"

class Database:

    def __init__(self, db_name: str = "mCubed", user: str = "mCubed", password: str = "crawling", host: str = "127.0.0.1", port: int = 5432 ) -> None:
        self._db_name: str = db_name
        self._user: str = user
        self._password: str = password
        self._host: str = host
        self._port: int = port

        self.connection = None
        self.error = None
        self.page_type_codes = [DB_Page_Types.HTML, DB_Page_Types.BINARY, DB_Page_Types.DUPLICATE, DB_Page_Types.FRONTIER]
        self.data_type_codes = [DB_Data_Types.PDF, DB_Data_Types.DOC, DB_Data_Types.DOCX, DB_Data_Types.PPT, DB_Data_Types.PPTX]

        self._create_connection()


    def _create_connection(self) -> None:
        try:
            self.connection = psycopg2.connect(dbname = self._db_name, host = self._host, port = self._port, user = self._user, password = self._password)
            self.connection.autocommit = True
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")
            self.error = e

    # INSERT functions
    # most single row insert functions return the id of the inserted row, or -1 if error occurs
    # multiple row insert function return True if insert was successfull or False if error occurs
    def insert_site(self, cursor, domain: str, robots_content: str, sitemap_content: str) -> int:
        sql = """INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s) RETURNING id"""
        
        if(domain is None or len(domain) == 0):
            print("Error inserting 'site', attribute 'domain' is empty.")
            return -1

        if(len(domain) > 500):
            print(f"Error inserting 'site', attribute 'domain' too long ({domain}).")
            return -1
        
        record = (domain, robots_content, sitemap_content)
        
        try:
            cursor.execute(sql, record)
            id = cursor.fetchone()[0]
            return id
        except Exception as e:
            print(f"Error inserting 'site': {e}")
            return -1
        
    def insert_site_many(self, cursor, values: list[tuple[str, str, str]]) -> bool:
        # a list of tuples must have attributes in the same order as above function insert_site
        sql = """INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s)"""

        for record in values:
            domain = record[0]
            if(domain is None or len(domain) == 0):
                print("Error inserting 'site', attribute 'domain' is empty.")
                return False

            if(len(domain) > 500):
                print(f"Error inserting 'site', attribute 'domain' too long ({domain}).")
                return False
            
        records = values

        try:
            cursor.executemany(sql, records)
            return True
        except Exception as e:
            print(f"Error inserting 'site': {e}")
            return False
        
    def insert_page(self, cursor, site_id: int, page_type_code: str, url: str, html_content: str, http_status_code: int, accessed_time: datetime, html_content_hash: str) -> int:
        sql = """INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time, html_content_hash) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"""

        site = self.get_site(cursor, site_id)
        if(site is None):
            print(f"Error inserting 'page', site with id {site_id} does not exist.")
            return -1
        
        if(page_type_code not in self.page_type_codes):
            print(f"Error inserting 'page', invalid page type code {page_type_code}.")
            return -1
        
        if(len(url) > 3000):
            print(f"Error inserting 'page', attribute 'url' too long ({url}).")
            return -1
        
        record = (site_id, page_type_code, url, html_content, http_status_code, accessed_time, html_content_hash)

        try:
            cursor.execute(sql, record)
            id = cursor.fetchone()[0]
            return id
        except Exception as e:
            print(f"Error inserting 'page': {e}")
            return -1
        
    def insert_image(self, cursor, page_id: int, filename: str, content_type: str, data: bytes, accessed_time: datetime) -> int:
        sql = """INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (%s, %s, %s, %s, %s) RETURNING id"""

        page = self.get_page(cursor, page_id)
        if(page is None):
            print(f"Error inserting 'image', page with id {page_id} does not exist.")
            return -1
        
        if(len(filename) > 255):
            print(f"Error inserting 'image', attribute 'filename' too long ({filename}).")
            return -1
        
        if(len(content_type) > 50):
            print(f"Error inserting 'image', attribute 'content_type' too long ({content_type}).")
            return -1
        
        record = (page_id, filename, content_type, data, accessed_time)

        try:
            cursor.execute(sql, record)
            id = cursor.fetchone()[0]
            return id
        except Exception as e:
            print(f"Error inserting 'image': {e}")
            return -1
        
    def insert_image_many(self, cursor, values: list[tuple[int, str, str, bytes, datetime]]) -> bool:
        sql = """INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (%s, %s, %s, %s, %s)"""

        page_ids = tuple(set(tuple(record[0] for record in values))) # take only unique elements
        page_ids_ok = self.check_page_ids(cursor, page_ids)
        if(not page_ids_ok):
            print("Error inserting 'image', page with given page_id does not exist.")
            return False

        for record in values:
            filename = record[1]
            content_type = record[2]

            if(len(filename) > 255):
                print(f"Error inserting 'image', attribute 'filename' too long ({filename}).")
                return False
        
            if(len(content_type) > 50):
                print(f"Error inserting 'image', attribute 'content_type' too long ({content_type}).")
                return False
            
        records = values

        try:
            cursor.executemany(sql, records)
            return True
        except Exception as e:
            print(f"Error inserting 'image': {e}")
            return False

    def insert_link(self, cursor, from_page: int, to_page: int) -> bool:
        sql = """INSERT INTO crawldb.link (from_page, to_page) VALUES(%s, %s)"""

        page_ids = tuple(set((from_page, to_page))) # take only unique elements
        page_ids_ok = self.check_page_ids(cursor, page_ids)
        if(not page_ids_ok):
            print("Error inserting 'link', page with given page_id does not exist.")
            return False
        
        record = (from_page, to_page)

        try:
            cursor.execute(sql, record)
            return True
        except Exception as e:
            print(f"Error inserting 'link': {e}")
            return False
        
    def insert_link_many(self, cursor, values: list[tuple[int, int]]) -> bool:
        sql = """INSERT INTO crawldb.link (from_page, to_page) VALUES(%s, %s)"""

        page_ids = tuple(set(tuple(page_id for tpl in values for page_id in tpl))) # take only unique elements
        page_ids_ok = self.check_page_ids(cursor, page_ids)
        if(not page_ids_ok):
            print("Error inserting 'image', page with given page_id does not exist.")
            return False
        
        records = values

        try:
            cursor.executemany(sql, records)
            return True
        except Exception as e:
            print(f"Error inserting 'link': {e}")
            return False
    
    def insert_page_data(self, cursor, page_id: int, data_type_code: str, data: bytes) -> int:
        sql = """INSERT INTO crawldb.page_data (page_id, data_type_code, data) VALUES (%s, %s, %s) RETURNING id"""

        page = self.get_page(cursor, page_id)
        if(page is None):
            print(f"Error inserting 'page_data', page with id {page_id} does not exist.")
            return -1
        
        if(data_type_code not in self.data_type_codes):
            print(f"Error inserting 'page_data', invalid data type code {data_type_code}.")
            return -1
        
        record = (page_id, data_type_code, data)

        try:
            cursor.execute(sql, record)
            id = cursor.fetchone()[0]
            return id
        except Exception as e:
            print(f"Error inserting 'page_data': {e}")
            return -1

    def insert_page_data_many(self, cursor, values: list[tuple[int, str, bytes]]) -> bool:
        sql = """INSERT INTO crawldb.page_data (page_id, data_type_code, data) VALUES (%s, %s, %s)"""

        page_ids = tuple(set(tuple(record[0] for record in values))) # take only unique elements
        page_ids_ok = self.check_page_ids(cursor, page_ids)
        if(not page_ids_ok):
            print("Error inserting 'page_data', page with given page_id does not exist.")
            return False
        
        data_type_codes = [record[1] for record in values]
        if(not set(data_type_codes).issubset(self.data_type_codes)):
            print("Error inserting 'page_data', invalid data type code.")
            return False
        
        records = values

        try:
            cursor.executemany(sql, records)
            return True
        except Exception as e:
            print(f"Error inserting 'page_data': {e}")
            return False


    # SELECT functions
    def get_site(self, cursor, id: int):
        sql = """SELECT * FROM crawldb.site WHERE id = %s"""

        try:
            cursor.execute(sql, (id,))
            site = cursor.fetchone()
            return site
        except Exception as e:
            print(f"Error selecting 'site': {e}")
            return False
        
    def get_site_name(self, cursor, domain: int):
        sql = """SELECT * FROM crawldb.site WHERE domain = %s"""

        try:
            cursor.execute(sql, (domain,))
            site = cursor.fetchone()
            return site
        except Exception as e:
            print(f"Error selecting 'site': {e}")
            return False
    
    def get_page(self, cursor, page_id: int):
        sql = """SELECT * FROM crawldb.page WHERE id = %s"""

        try:
            cursor.execute(sql, (page_id,))
            page = cursor.fetchone()
            return page
        except Exception as e:
            print(f"Error selecting 'page': {e}")
            return False
        
    def get_page_by_hash(self, cursor, html_content_hash: str):
        sql = """SELECT * FROM crawldb.page WHERE html_content_hash = %s"""

        try:
            cursor.execute(sql, (html_content_hash,))
            page = cursor.fetchone()
            return page
        except Exception as e:
            print(f"Error selecting 'page': {e}")
            return False
        
    def get_page_by_url(self, cursor, url: str):
        sql = """SELECT * FROM crawldb.page WHERE url = %s"""

        try:
            cursor.execute(sql, (url,))
            page = cursor.fetchone()
            return page
        except Exception as e:
            print(f"Error selecting 'page': {e}")
            return False


    # OTHER
    def check_page_ids(self, cursor, page_ids):
        sql = """SELECT COUNT(*) FROM crawldb.page WHERE id IN %s"""

        try:
            cursor.execute(sql, (page_ids,))
            res = cursor.fetchone()
            return res[0] == len(page_ids)
        except Exception as e:
            print(f"Error selecting 'page': {e}")
            return False