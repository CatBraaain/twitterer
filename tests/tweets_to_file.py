import os
import sys
from pathlib import Path

# from snoop import pp, snoop

os.chdir(Path(__file__).parent)
sys.path.append("../src")

from twitterer import Twitterer  # type: ignore # noqa: E402


# @snoop()
def main() -> None:
    twitterer = Twitterer(headless=False)
    twitterer.authenticate()
    tweets = list(
        twitterer.get_tweets(
            url="https://x.com/search?q=funny%20min_retweets:1000%20filter:videos",
            max_tweets=10,
        )
    )

    twitterer.save_to_file(tweets)


main()
