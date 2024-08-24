import os
import sys
from pathlib import Path

# from snoop import pp, snoop

os.chdir(Path(__file__).parent)
sys.path.append("../src")

from twitterer import Twitterer  # type: ignore[import-not-found] # noqa: E402


# @snoop()
def main() -> None:
    twitterer = Twitterer(headless=False)
    twitterer.authenticate()
    tweets = list(
        twitterer.get_tweets(
            url="https://x.com/search?q=min_retweets:5000+filter:videos&f=live",
            max_tweet_count=10,
            # url="https://x.com/search?q=min_retweets:250000%20filter:videos",
            # max_tweet_count=sys.maxsize,
            # url="https://x.com/search?q=min_retweets:1000000%20filter:videos",
            # max_tweet_count=sys.maxsize,
            # url="https://x.com/search?q=min_retweets:5000+filter:videos&f=live",
            # max_tweet_count=sys.maxsize,
        )
    )

    twitterer.save_to_file(tweets)


main()
