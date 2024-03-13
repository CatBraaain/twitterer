from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from const import *
from tweet import Tweet


class Collector:
    def __init__(self, driver):
        self.driver = driver
        self.max_tweets = 50
        self.tweets = []
        self.tweet_elements = []

    def get_tweets(self, url, max_tweets=50):
        self.tweets = []
        self.tweet_elements = []
        self.max_tweets = max_tweets

        self.driver.get(url)

        while not (self._reached_max()) and (
            new_tweet_element := self._wait_for_next_tweet_element()
        ):
            new_tweet = Tweet(new_tweet_element)

            self.tweet_elements.append(new_tweet_element)
            self.tweets.append(new_tweet)
            yield new_tweet

            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", new_tweet_element
            )

    def _reached_max(self):
        reached_max = len(self.tweets) >= self.max_tweets
        if reached_max:
            print("got enough tweets")

        return reached_max

    def _wait_for_next_tweet_element(self):
        if self._is_loading():
            WebDriverWait(self.driver, 10).until_not(self._is_loading)

        try:
            new_tweet_element = WebDriverWait(self.driver, 5).until(
                self._get_new_tweet_element
            )
        except:
            print("no more tweets")
            new_tweet_element = None
        return new_tweet_element

    def _is_loading(self, _=None):
        is_loading = bool(self.driver.find_elements(By.CSS_SELECTOR, Selector.LOADING))
        return is_loading

    def _get_new_tweet_element(self, _=None):
        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, Selector.BASE)
        new_tweet_elements = [e for e in tweet_elements if e not in self.tweet_elements]
        # new_tweet_element = (new_tweet_elements or [None])[0]
        new_tweet_element = new_tweet_elements[0] if new_tweet_elements else None
        return new_tweet_element
