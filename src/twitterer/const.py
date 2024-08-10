import os
from typing import Final

from dotenv import find_dotenv, load_dotenv

env_path = find_dotenv(usecwd=True)
if not (env_path):
    raise Exception("Could not find env file to use authenticate")
load_dotenv(env_path, override=True)

TWITTER_LOGIN_URL: Final[str] = "https://x.com/i/flow/login"
# TWITTER_REDIRECT_URL: Final[str] = "https://x.com/i/flow/login?redirect_after_login=%2Fhome"
TWITTER_HOME_URL: Final[str] = "https://x.com/home"

TWITTER_USERNAME: Final[str | None] = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD: Final[str | None] = os.getenv("TWITTER_PASSWORD")

COOKIES_PATH: Final[str] = "twitter_cookie.pkl"


class Selector:
    USERNAME: Final[str] = "input[autocomplete='username']"
    PASSWORD: Final[str] = "input[autocomplete='current-password']"

    LOGIN_SUCCESSED: Final[str] = "[data-testid='SideNav_AccountSwitcher_Button']"
    LOGIN_FAILED: Final[str] = "[data-testid='mask']"

    LOADING: Final[str] = "circle[style^='stroke']"
    BASE: Final[str] = "[data-testid='tweet']"

    URL: Final[str] = "a[href*='/status/']:not([href$='analytics'])"
    USER_ELEMENTS: Final[str] = "[data-testid='User-Name'] a"
    VERIFIED: Final[str] = "[data-testid='icon-verified']"
    DATE_TIME: Final[str] = "time[datetime]"

    CONTENT: Final[str] = "[data-testid='tweetText'] span,[data-testid='tweetText'] img"

    REPLYS: Final[str] = "[data-testid='reply']"

    UNRETWEETED: Final[str] = "[data-testid='retweet']"
    RETWEETED: Final[str] = "[data-testid='unretweet']"
    RETWEETS: Final[str] = f"{UNRETWEETED},{RETWEETED}"
    RETWEET_CONFIRM: Final[str] = "[data-testid='retweetConfirm']"
    UNRETWEET_CONFIRM: Final[str] = "[data-testid='unretweetConfirm']"

    UNLIKED: Final[str] = "[data-testid='like']"
    LIKED: Final[str] = "[data-testid='unlike']"
    LIKES: Final[str] = f"{UNLIKED},{LIKED}"

    ANALYTICS: Final[str] = "a[href*='/status/'][href$='/analytics']"
    BOOKMARKS: Final[str] = "[data-testid='bookmark']"

    IMGS: Final[str] = (
        "[data-testid='tweetPhoto'][src^='https://pbs.twimg.com/media/'] img"
    )
    VIDEOS: Final[str] = (
        "[data-testid='videoPlayer'],[data-testid='previewInterstitial']"
    )
    VIDEO_THUMBNAILS: Final[str] = (
        "[data-testid='videoPlayer'] video,[data-testid='previewInterstitial'] img"
    )


# $$("[data-testid='tweet']")
# $$("[data-testid='icon-verified']")
# $$("[data-testid='Tweet-User-Avatar']")
# $$("[data-testid='UserAvatar-Container-xxx']")
# $$("[data-testid='User-Name']")
# $$("[data-testid='caret']")
# $$("[data-testid='tweetText']")
# $$("[data-testid='reply']")
# $$("[data-testid='app-text-transition-container']")
# $$("[data-testid='retweet']")
# $$("[data-testid='like']")
# $$("[data-testid='bookmark']")
# $$("[data-testid='tweetPhoto']")
# $$("[data-testid='placementTracking']")
# $$("[data-testid='videoPlayer']")
# $$("[data-testid='videoComponent']")
