from typing import Generator, Optional

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from . import const
from .tweet import Tweet


class Collector:
    driver: WebDriver
    max_tweets: int
    tweets: list[Tweet]
    tweet_elements: list[WebElement]

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.max_tweets = 50
        self.tweets = []
        self.tweet_elements = []

    def get_tweets(
        self, url: str, max_tweets: int = 50
    ) -> Generator[Tweet, None, None]:
        self.tweets = []
        self.tweet_elements = []
        self.max_tweets = max_tweets

        self.driver.get(url)

        while not (self._reached_max()) and (
            new_tweet_element := self._wait_for_next_tweet_element()
        ):
            new_tweet = Tweet(self.driver, new_tweet_element)

            self.tweet_elements.append(new_tweet_element)
            self.tweets.append(new_tweet)
            yield new_tweet

            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", new_tweet_element
            )

    def _reached_max(self) -> bool:
        reached_max = len(self.tweets) >= self.max_tweets
        if reached_max:
            print(f"got {len(self.tweets)}/{self.max_tweets} tweets")
            print("reached max tweets")

        return reached_max

    def _wait_for_next_tweet_element(self) -> Optional[WebElement]:
        if self._is_loading():
            WebDriverWait(self.driver, 10).until_not(self._is_loading)

        try:
            new_tweet_element: Optional[WebElement] = WebDriverWait(
                self.driver, 5
            ).until(self._get_new_tweet_element)
        except NoSuchElementException:
            print(f"got {len(self.tweets)}/{self.max_tweets} tweets")
            print("no more tweets")
            new_tweet_element = None
        return new_tweet_element

    def _is_loading(self, _: Optional[WebDriver] = None) -> bool:
        is_loading = bool(
            self.driver.find_elements(By.CSS_SELECTOR, const.Selector.LOADING)
        )
        return is_loading

    def _get_new_tweet_element(
        self, _: Optional[WebDriver] = None
    ) -> Optional[WebElement]:
        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, const.Selector.BASE)
        new_tweet_elements = [e for e in tweet_elements if e not in self.tweet_elements]
        # new_tweet_element = (new_tweet_elements or [None])[0]
        new_tweet_element = new_tweet_elements[0] if new_tweet_elements else None
        return new_tweet_element
