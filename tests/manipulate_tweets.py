import os
import sys
from pathlib import Path
from time import sleep

# from snoop import pp, snoop

os.chdir(Path(__file__).parent)
sys.path.append("../src")

from twitterer import Twitterer  # type: ignore[import-not-found] # noqa: E402


# @snoop()
def main() -> None:
    twitterer = Twitterer(headless=False)
    twitterer.authenticate()
    for tweet in twitterer.get_tweets(
        url="https://x.com/search?q=funny%20min_retweets:1000%20filter:videos",
        max_tweet_count=1,
    ):
        tweet.like()
        sleep(1)
        tweet.unlike()
        sleep(1)
        tweet.retweet()
        sleep(1)
        tweet.unretweet()


main()
