from typing import Generator, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait

from . import const
from .tweet import Tweet


class Collector:
    driver: WebDriver
    max_tweets: int
    tweets: list[Tweet]

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.tweets = []

    def get_tweets(
        self, url: str, max_tweets: int = 50
    ) -> Generator[Tweet, None, None]:
        self.tweets = []
        self.max_tweets = max_tweets

        self.driver.get(url)

        while True:
            if self._has_enough_tweets:
                print(f"Got {len(self.tweets)}/{self.max_tweets} tweets")
                print("Successfully retrieved the specified number of tweets.")
                break
            try:
                new_tweet: Tweet = WebDriverWait(self.driver, float("inf")).until(
                    lambda _: self._get_new_tweet()
                )  # type: ignore[assignment] # cuz `.until()` returns truthy
            except TimeoutException:
                print(f"Got {len(self.tweets)}/{self.max_tweets} tweets.")
                print("Reached the bottom of the page and no more tweets available.")
                break

            self.tweets.append(new_tweet)
            yield new_tweet

    @property
    def _has_enough_tweets(self) -> bool:
        return len(self.tweets) >= self.max_tweets

    def _get_new_tweet(self) -> Optional[Tweet]:
        if not self._is_at_bottom:
            new_tweet = self._find_new_tweet()
        else:
            new_tweet = WebDriverWait(self.driver, 5).until(
                lambda _: self._find_new_tweet()
            )
        return new_tweet

    @property
    def _is_at_bottom(self) -> bool:
        return self.driver.execute_script(
            "return Math.abs(document.body.scrollHeight - window.innerHeight - window.scrollY) < 100;"
        )

    def _find_new_tweet(self) -> Optional[Tweet]:
        WebDriverWait(self.driver, 10).until_not(lambda _: self._is_loading)

        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, const.Selector.BASE)
        tweets = [Tweet(self.driver, tweet_element) for tweet_element in tweet_elements]
        new_tweets = [tweet for tweet in tweets if tweet not in self.tweets]

        if new_tweets:
            new_tweet = new_tweets[0]
            self._scroll_to_element(new_tweet.element)
        else:
            new_tweet = None
            self._scroll_to_element(tweets[-1].element)

        return new_tweet

    @property
    def _is_loading(self) -> bool:
        return bool(self.driver.find_elements(By.CSS_SELECTOR, const.Selector.LOADING))

    def _scroll_to_element(self, element: WebElement) -> None:
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
