from typing import Generator, Optional

from selenium.common.exceptions import TimeoutException
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

        while True:
            if self._has_enough_tweets:
                print(f"Got {len(self.tweets)}/{self.max_tweets} tweets")
                print("Successfully retrieved the specified number of tweets.")
                break
            try:
                new_tweet_element: WebElement = self._wait_for_next_tweet_element()  # type: ignore[assignment] # cuz `.until()` returns truthy
            except TimeoutException:
                print(f"Got {len(self.tweets)}/{self.max_tweets} tweets.")
                print("Reached the bottom of the page and no more tweets available.")
                break

            new_tweet = Tweet(self.driver, new_tweet_element)

            self.tweet_elements.append(new_tweet_element)
            self.tweets.append(new_tweet)
            yield new_tweet

            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", new_tweet_element
            )

    @property
    def _has_enough_tweets(self) -> bool:
        return len(self.tweets) >= self.max_tweets

    def _wait_for_next_tweet_element(self) -> Optional[WebElement]:
        if self._is_loading:
            WebDriverWait(self.driver, 10).until_not(lambda _: self._is_loading)

        new_tweet_element: Optional[WebElement] = None
        new_tweet_element = WebDriverWait(self.driver, 5).until(
            self._get_new_tweet_element
        )
        return new_tweet_element

    @property
    def _is_loading(self) -> bool:
        return bool(self.driver.find_elements(By.CSS_SELECTOR, const.Selector.LOADING))

    def _get_new_tweet_element(
        self, _: Optional[WebDriver] = None
    ) -> Optional[WebElement]:
        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, const.Selector.BASE)
        new_tweet_elements = [e for e in tweet_elements if e not in self.tweet_elements]
        # new_tweet_element = (new_tweet_elements or [None])[0]
        new_tweet_element = new_tweet_elements[0] if new_tweet_elements else None
        return new_tweet_element
