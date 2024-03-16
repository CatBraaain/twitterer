import os
from pathlib import Path

from snoop import pp, snoop

os.chdir(Path(__file__).parent)

from twitterer import Twitterer


@snoop()
def main():
    twitterer = Twitterer()
    twitterer.authenticate()
    tweets = list(
        twitterer.get_tweets(
            url="https://twitter.com/search?q=cat%20min_retweets%3A10000%20filter%3Avideos",
            max_tweets=1,
        )
    )

    twitterer.save_to_file(tweets)


main()
