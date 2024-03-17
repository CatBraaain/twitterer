import os
from pathlib import Path

# from snoop import pp, snoop

os.chdir(Path(__file__).parent)

from twitterer import Twitterer


# @snoop()
def main():
    twitterer = Twitterer(headless=True)
    twitterer.authenticate()
    tweets = list(
        twitterer.get_tweets(
            url="https://twitter.com/search?q=funny%20min_retweets:1000%20filter:videos",
            max_tweets=10,
        )
    )

    twitterer.save_to_file(tweets)


main()
