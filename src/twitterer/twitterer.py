import datetime
from pathlib import Path
from typing import Generator, List, Optional

import jsonpickle
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from .authenticator import Authenticator
from .collector import Collector
from .tweet import Tweet


class Twitterer:
    driver: WebDriver

    def __init__(self, headless: bool = True) -> None:
        self.driver = self._get_driver(headless)

    def _get_driver(self, headless: bool = True) -> WebDriver:
        options = Options()
        # options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        # options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")
        options.add_argument(f"--user-agent={UserAgent().chrome}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("detach", not headless)

        if headless:
            options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

        return driver

    def authenticate(self) -> None:
        Authenticator(self.driver).authenticate()

    def get_tweets(self, url: str, max_tweets: int) -> Generator[Tweet, None, None]:
        yield from Collector(self.driver).get_tweets(url, max_tweets)

    def save_to_file(self, tweets: List[Tweet], out_path: Optional[str] = None) -> None:
        if out_path is None:
            out_path = f"output\\tweets_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')[:-3]}.json"

        tweets_json = jsonpickle.encode(tweets, unpicklable=False, indent=4)

        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open(mode="x") as f:
            f.write(tweets_json)
        pass
