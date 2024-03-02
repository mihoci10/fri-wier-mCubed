from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from time import sleep


class Extractor:

    def __init__(self, load_time: float = 5) -> None:
        self.load_time: float = load_time

        self.firefox_options: FirefoxOptions = FirefoxOptions()
        # firefox_options.add_argument("--headless")
        self.firefox_options.add_argument("user-agent=fri-ieps-mCubed")

    def run(self, URL: str) -> None:
        with webdriver.Firefox(options=self.firefox_options) as driver: 
            
            driver.get(URL)
            sleep(self.load_time)

            content = driver.page_source
            print(content)
