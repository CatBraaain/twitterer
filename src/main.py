from snoop import pp, snoop

from twitterer import Twitterer


@snoop()
def main():
    twitterer = Twitterer()
    twitterer.authenticate()
    twitterer.driver.get(
        "https://twitter.com/search?q=cat%20min_retweets%3A10000%20filter%3Avideos"
    )
    tweets = list(twitterer.get_tweets({"max_tweets": 50}))


main()
