import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from time import sleep
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from utils import get_hostname_from_URL, get_scheme_from_URL
import urllib.request
from datetime import datetime

class Extractor:

    def __init__(self, load_time: float = 5) -> None:
        self.load_time: float = load_time

        self.firefox_options: FirefoxOptions = FirefoxOptions()
        # firefox_options.add_argument("--headless")
        self.firefox_options.add_argument("user-agent=fri-ieps-mCubed")

        self.url = None
        self.content = None
        self.content_hash = None
        self.http_status = None
        self.accessed_time = None
        self.permission = False
        self.time_delay = None
        self.domain = None
        self.robots_content = None
        self.sitemap_content = None

    def run(self, URL: str) -> None:
        self._check_compliance(URL)

        self.url = URL
        self.content = None
        self.content_hash = None
        self.http_status = None
        self.accessed_time = datetime.now()

        if not self.permission:
            return
        
        with webdriver.Firefox(options=self.firefox_options) as driver: 
            driver.get(URL)
            sleep(self.load_time)
            self.content = driver.page_source
            self.content_hash = str(hash(self.content))
            self.http_status = self._get_response_code_simple(URL)

    def _get_content_simple(self, URL):
        result = None
        try:
            content = urllib.request.urlopen(URL)
            result = content.read().decode('utf-8')
        except Exception as e:
            pass
        return result
    
    def _get_response_code_simple(self, URL):
        result = None
        try:
            content = urllib.request.urlopen(URL)
            result = content.getcode()
        except Exception as e:
            pass
        return result


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
            
    def extract_links_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', href=True)
        binary_file_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
        extracted_urls = []
        for link in links:
            url = link['href']
            if url.startswith('http') or url.startswith('https'):
                extracted_urls.append(url)
            if any(url.endswith(ext) for ext in binary_file_extensions):
                continue
                #TODO: set page_type to BINARY
        return extracted_urls

    def extract_links_from_file(self, input_file):
        print("Extracting URLs from file")
        new_urls = []

        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                html_content = file.read()

            existing_urls = set()
            if os.path.exists('Assignment1/urls.txt'):
                with open('Assignment1/urls.txt', 'r', encoding='utf-8') as url_file:
                    existing_urls = set(line.strip() for line in url_file)

            extracted_urls = self.extract_links_from_html(html_content)

            for url in extracted_urls:
                if url not in existing_urls:
                    new_urls.append(url)
                    existing_urls.add(url)

            if new_urls:
                with open('Assignment1/urls.txt', 'a', encoding='utf-8') as file:
                    for url in new_urls:
                        file.write(url + '\n')
                print(f"{len(new_urls)} new URLs added to urls.txt")
            else:
                print("No new URLs found.")

        except FileNotFoundError:
            print(f"File '{input_file}' not found.")


