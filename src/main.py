from snoop import pp, snoop

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
