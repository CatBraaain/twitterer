from typing import Generator, Optional

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait

from . import const
from .scraping_progress import ScrapingProgress
from .tweet import Tweet


class Collector:
    driver: WebDriver
    max_tweet_count: int
    tweets: list[Tweet]

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.tweets = []

    def get_tweets(
        self, url: str, max_tweet_count: int = 50
    ) -> Generator[Tweet, None, None]:
        self.tweets = []
        self.max_tweet_count = max_tweet_count

        self.driver.get(url)

        progress = ScrapingProgress(url, max_tweet_count)

        while True:
            if self._has_enough_tweets:
                progress.stop_on_got_enough()
                break

            try:
                new_tweet: Tweet = WebDriverWait(self.driver, float("inf")).until(
                    lambda _: self._find_new_tweet()
                )  # type: ignore[assignment] # cuz `.until()` returns truthy
            except TweetsRanOut:
                progress.stop_on_got_all()
                break
            except TweetsEmpty:
                progress.stop_on_empty()
                break
            except StaleElementReferenceException:
                continue

            progress.advance_scraping()
            self.tweets.append(new_tweet)
            yield new_tweet

    @property
    def _has_enough_tweets(self) -> bool:
        return len(self.tweets) >= self.max_tweet_count

    def _find_new_tweet(self) -> Optional[Tweet]:
        WebDriverWait(self.driver, 10).until_not(lambda _: self._is_loading)

        if not self._is_at_bottom:
            new_tweet = self._scrape_new_tweet()
        else:
            try:
                new_tweet = WebDriverWait(self.driver, 5).until(
                    lambda _: self._scrape_new_tweet()
                )
            except TimeoutException:
                raise TweetsRanOut()
            except TweetsEmpty:
                raise TweetsEmpty()
        return new_tweet

    @property
    def _is_loading(self) -> bool:
        return bool(self.driver.find_elements(By.CSS_SELECTOR, const.Selector.LOADING))

    @property
    def _is_at_bottom(self) -> bool:
        return self.driver.execute_script(
            "return Math.abs(document.body.scrollHeight - window.innerHeight - window.scrollY) < 100;"
        )

    def _scrape_new_tweet(self) -> Optional[Tweet]:
        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, const.Selector.BASE)
        if not tweet_elements:
            if self.driver.find_elements(By.CSS_SELECTOR, const.Selector.EMPTY_STATE):
                raise TweetsEmpty()

        collected_tweet_urls = [tweet.url for tweet in self.tweets]
        new_tweet_elements = [
            tweet_element
            for tweet_element in tweet_elements
            if tweet_element.find_element(
                By.CSS_SELECTOR, const.Selector.URL
            ).get_attribute("href")
            not in collected_tweet_urls
        ]
        if new_tweet_elements:
            new_tweet = Tweet(self.driver, new_tweet_elements[0])
            self._scroll_to_element(new_tweet.element)
        else:
            new_tweet = None
            self._scroll_to_element(tweet_elements[-1])

        return new_tweet

    def _scroll_to_element(self, element: WebElement) -> None:
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)


class TweetsRanOut(Exception):
    def __init__(self, msg: str = "No more tweets available on this page.") -> None:
        super().__init__(msg)


class TweetsEmpty(Exception):
    def __init__(self, msg: str = "No results found for the query") -> None:
        super().__init__(msg)
