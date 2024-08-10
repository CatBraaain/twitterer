import os
from pathlib import Path
from time import sleep

# from snoop import pp, snoop

os.chdir(Path(__file__).parent)

from twitterer import Twitterer


# @snoop()
def main():
    twitterer = Twitterer(headless=False)
    twitterer.authenticate()
    for tweet in twitterer.get_tweets(
        url="https://x.com/search?q=funny%20min_retweets:1000%20filter:videos",
        max_tweets=1,
    ):
        tweet.like()
        sleep(1)
        tweet.unlike()
        sleep(1)
        tweet.retweet()
        sleep(1)
        tweet.unretweet()


main()
