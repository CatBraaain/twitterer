# twitterer

Python's package to scrape Twitter with selenium.
Get, like, retweet tweets with automatically.

## Usage
1. Install python package
```cmd
pip install twitterer
```
2. Create `.env` file at project root.
```properties
TWITTER_USERNAME = ReplaceThisToYourOwns
TWITTER_PASSWORD = ReplaceThisToYourOwns
```

### Get tweets and save it
```python
from twitterer import Twitterer

twitterer = Twitterer()
twitterer.authenticate()
tweets = list(
    twitterer.get_tweets(
        url="https://twitter.com/search?q=funny%20filter:videos",
        max_tweets=20,
    )
)

twitterer.save_to_file(tweets)
```

### Like and retweet tweets
`.get_tweets()` method returns generator.
This is real-time processing, so when you use `.like()` or `.retweet()` method on tweets, i must be handled by a generator.
```python
from twitterer import Twitterer

twitterer = Twitterer(headless=False)
twitterer.authenticate()
for tweet in twitterer.get_tweets(
    url="https://twitter.com/home",
    max_tweets=20,
):
    tweet.like()
    tweet.retweet()
```

