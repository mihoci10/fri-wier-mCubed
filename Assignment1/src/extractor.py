import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from time import sleep
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from utils import get_hostname_from_URL, get_scheme_from_URL, get_canonical_URL
import urllib.request
from urllib import error, parse
from datetime import datetime
import ssl

class Extractor:

    def __init__(self, load_time: float = 5) -> None:
        self.load_time: float = load_time
        self._init_driver()

        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

        self.url = None
        self.content = None
        self.content_type = None
        self.content_hash = None
        self.http_status = None
        self.accessed_time = None
        self.permission = False
        self.time_delay = None
        self.domain = None
        self.robots_content = None
        self.sitemap_content = None
        self.extracted_urls: list[str] = []
        self.extracted_files: list[str] = []
        self.extracted_images: list[str] = []

    def _init_driver(self):
        firefox_options: FirefoxOptions = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("user-agent=fri-ieps-mCubed")
        firefox_options.accept_insecure_certs=True
        
        self.driver = webdriver.Firefox(options=firefox_options)

    def run(self, URL: str) -> None:
        self._check_compliance(URL)

        self.url = URL
        self.content = None
        self.content_type = None
        self.content_hash = None
        self.http_status = None
        self.accessed_time = datetime.now()
        self.extracted_urls = []
        self.extracted_files = []
        self.extracted_images = []

        if not self.permission:
            return
    
        self._get_response_info(URL)

        if (self.http_status // 100 != 2) or (self.content_type != None and self.content_type != 'text/html'):
            self.content = ''
            self.content_hash = ''
        else:
            try:
                self.driver.get(URL)
                sleep(self.load_time)
                self.content = self.driver.page_source
                self.content_hash = str(hash(self.content))
                self._extract_content(self.content)
            except Exception as e:
                self.content = ''
                self.content_hash = ''

    def _get_content_simple(self, URL):
        result = None
        try:
            content = urllib.request.urlopen(URL, context=self.ssl_ctx, timeout=2)
            result = content.read().decode('utf-8')
        except Exception as e:
            pass
        return result
    
    def _get_response_info(self, URL):
        self.http_status = None
        self.content_type = None
        try:
            content = urllib.request.urlopen(URL, context=self.ssl_ctx, timeout=2)
            self.content_type = content.info().get_content_type()
            self.http_status = content.getcode()
        except error.HTTPError as e:
            self.http_status = e.code
        except error.URLError as e:
            self.http_status = 408
        except Exception as e:
            self.http_status = 495


    def _check_compliance(self, URL: str):
        SCHEME = get_scheme_from_URL(URL)
        HOST_NAME = get_hostname_from_URL(URL)
        robots_url = f'{SCHEME}://{HOST_NAME}/robots.txt'

        self.permission = True
        self.time_delay = None
        self.domain = HOST_NAME
        self.robots_content = None
        self.sitemap_content = None

        robot_parser = RobotFileParser(robots_url)
        try:
            robot_parser.read()
            self.permission = robot_parser.can_fetch('fri-ieps-mCubed', URL)
            self.time_delay = robot_parser.crawl_delay('fri-ieps-mCubed')
            self.robots_content = self._get_content_simple(robots_url)
            if robot_parser.site_maps() != None and len(robot_parser.site_maps()) > 0:
                self.sitemap_content = self._get_content_simple(robot_parser.site_maps()[0])
        except Exception as e:
            print(f'extractor._check_compliance threw {e}')

    def _extract_content(self, content):
        self._extract_links_files_from_html(content)
        self._extract_images_from_html(content)

    def _extract_links_files_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', href=True)
        binary_file_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
        self.extracted_urls = []
        for link in links:
            url = link['href']
            url = parse.urljoin(self.url, url)
            url = get_canonical_URL(url)
            if any(url.endswith(ext) for ext in binary_file_extensions):
                self.extracted_files.append(url)
            elif url.startswith('http') or url.startswith('https'):
                self.extracted_urls.append(url)
            
    def _extract_images_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('img')
        self.extracted_images = []
        for link in links:
            url = link['src']
            url = parse.urljoin(self.url, url)
            if url.startswith('http') or url.startswith('https'):
                self.extracted_images.append(url)
