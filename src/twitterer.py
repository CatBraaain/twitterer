from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from authenticator import Authenticator
from collector import Collector
from const import *


class Twitterer:
    def __init__(self):
        self.driver = self._get_driver()

    def _get_driver(self):
        options = Options()
        # options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        # options.add_argument("--headless=new")
        options.add_argument("--ignore-certificate-errors")
        # options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")
        options.add_argument(f"--user-agent={UserAgent().chrome}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(options=options)

        return driver

    def authenticate(self):
        Authenticator(self.driver).authenticate()

    def get_tweets(self, url, max_tweets):
        yield from Collector(self.driver).get_tweets(url, max_tweets)
