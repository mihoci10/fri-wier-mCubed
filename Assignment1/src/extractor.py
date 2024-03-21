import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from time import sleep
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from utils import get_hostname_from_URL, get_scheme_from_URL

class Extractor:

    def __init__(self, load_time: float = 5) -> None:
        self.load_time: float = load_time

        self.firefox_options: FirefoxOptions = FirefoxOptions()
        # firefox_options.add_argument("--headless")
        self.firefox_options.add_argument("user-agent=fri-ieps-mCubed")

        self.content = None
        self.permission = False
        self.time_delay = None

    def run(self, URL: str) -> None:
        self._check_compliance(URL)

        self.content = None

        if not self.permission:
            return
        
        with webdriver.Firefox(options=self.firefox_options) as driver: 
            driver.get(URL)
            sleep(self.load_time)
            self.content = driver.page_source

    def _check_compliance(self, URL: str):
        SCHEME = get_scheme_from_URL(URL)
        HOST_NAME = get_hostname_from_URL(URL)
        
        self.permission = True
        self.time_delay = None

        robot_parser = RobotFileParser(f'{SCHEME}://{HOST_NAME}/robots.txt')
        try:
            robot_parser.read()
            self.permission = robot_parser.can_fetch('fri-ieps-mCubed', URL)
            self.time_delay = robot_parser.crawl_delay('fri-ieps-mCubed')

        except Exception as e:
            print(f'extractor.run threw {e}')
            
    def extract_links_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', href=True)
        extracted_urls = []
        for link in links:
            url = link['href']
            # You can add more filtering conditions as per your requirement
            if url.startswith('http') or url.startswith('https'):
                extracted_urls.append(url)
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


