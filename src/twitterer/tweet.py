import re
from dataclasses import dataclass
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from . import const


@dataclass
class User:
    name: str
    id: str
    verified: bool


@dataclass
class Statistic:
    replys: int
    retweets: int
    likes: int
    analytics: int
    bookmarks: int


@dataclass
class Status:
    is_liked: bool
    is_retweeted: bool


@dataclass
class Img:
    count: int
    urls: List[str]


@dataclass
class Video:
    count: int
    thumbnails: List[str]


class Media:
    def __init__(self, img: Img, video: Video):
        self.has_img = bool(img.count)
        self.img = img
        self.has_video = bool(video.count)
        self.video = video


class Tweet:
    driver: WebDriver
    __element: WebElement
    html: str
    __soup: BeautifulSoup
    url: str
    id: str
    date_time: str
    is_ad: bool
    user: User
    content: str
    replys: int
    retweets: int
    likes: int
    analytics: int
    bookmarks: int
    statistic: Statistic  # static => statics
    status: Status
    media: Media

    def __init__(self, driver: WebDriver, element: WebElement) -> None:
        self.driver = driver

        html = element.get_attribute("outerHTML")
        if html is None:
            raise TypeError
        soup = BeautifulSoup(html, "lxml")

        self.__element = element
        self.html = html
        self.__soup = soup

        try:
            self.url = "https://x.com" + (
                soup.select_one(const.Selector.URL).get("href")
            )
        except AttributeError:
            self.url = "https://x.com" + (
                soup.select_one(const.Selector.ANALYTICS)
                .get("href")
                .removesuffix("/analytics")
            )
        self.id = self.url.split("/")[-1]

        try:
            self.date_time = soup.select_one(const.Selector.DATE_TIME).get("datetime")
        except AttributeError:
            self.date_time = ""
        self.is_ad = False if self.date_time else True

        user_elements = soup.select(const.Selector.USER_ELEMENTS)
        self.user = User(
            name=user_elements[0].text,
            id=user_elements[1].text.removeprefix("@"),
            verified=bool(soup.select(const.Selector.VERIFIED)),
        )

        content_elements = soup.select(const.Selector.CONTENT)
        content_extractor_map = {
            "span": (lambda e: e.text),
            "img": (lambda e: e.get("alt")),
        }
        self.content = "".join(
            [content_extractor_map[e.name](e) for e in content_elements]
        )

        replys = re.sub(
            "[^\\d]", "0", soup.select_one(const.Selector.REPLYS).get("aria-label")
        )
        retweets = re.sub(
            "[^\\d]", "0", soup.select_one(const.Selector.RETWEETS).get("aria-label")
        )
        likes = re.sub(
            "[^\\d]", "0", soup.select_one(const.Selector.LIKES).get("aria-label")
        )
        try:
            analytics = re.sub(
                "[^\\d]",
                "0",
                soup.select_one(const.Selector.ANALYTICS).get("aria-label"),
            )
        except AttributeError:
            analytics = "0"
        bookmarks = re.sub(
            "[^\\d]",
            "0",
            soup.select_one(const.Selector.BOOKMARKS).get("aria-label"),
        )

        self.statistic = Statistic(
            replys=int(replys),
            retweets=int(retweets),
            likes=int(likes),
            analytics=int(analytics),
            bookmarks=int(bookmarks),
        )

        self.status = Status(
            is_liked=bool(soup.select(const.Selector.LIKED)),
            is_retweeted=bool(soup.select(const.Selector.RETWEETED)),
        )

        thumbnail_elements = soup.select(const.Selector.VIDEO_THUMBNAILS)
        thumbnail_extractor_map = {
            "video": (lambda e: e.get("poster")),
            "img": (lambda e: e.get("src")),
        }
        thumbnails = [thumbnail_extractor_map[e.name](e) for e in thumbnail_elements]
        self.media = Media(
            img=Img(
                count=len(soup.select(const.Selector.IMGS)),
                urls=[e.get("src") for e in soup.select(const.Selector.IMGS)],
            ),
            video=Video(
                count=len(soup.select(const.Selector.VIDEOS)), thumbnails=thumbnails
            ),
        )

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        del state["_Tweet__element"]
        del state["html"]
        del state["_Tweet__soup"]
        del state["driver"]

        return state

    def like(self) -> None:
        self.driver.implicitly_wait(10)
        try:
            self.__element.find_element(By.CSS_SELECTOR, const.Selector.UNLIKED).click()
        except NoSuchElementException:
            print(f"failed to like a tweet {self.id=}")
        self.driver.implicitly_wait(0)

    def unlike(self) -> None:
        self.driver.implicitly_wait(10)
        try:
            self.__element.find_element(By.CSS_SELECTOR, const.Selector.LIKED).click()
        except (NoSuchElementException, ElementNotInteractableException):
            print(f"failed to unlike a tweet {self.id=}")
        self.driver.implicitly_wait(0)

    def retweet(self) -> None:
        self.driver.implicitly_wait(10)
        try:
            self.__element.find_element(
                By.CSS_SELECTOR, const.Selector.UNRETWEETED
            ).click()
            self.driver.find_element(
                By.CSS_SELECTOR, const.Selector.RETWEET_CONFIRM
            ).click()
        except (NoSuchElementException, ElementNotInteractableException):
            print(f"failed to retweet a tweet {self.id=}")
        self.driver.implicitly_wait(0)

    def unretweet(self) -> None:
        self.driver.implicitly_wait(10)
        try:
            self.__element.find_element(
                By.CSS_SELECTOR, const.Selector.RETWEETED
            ).click()
            self.driver.find_element(
                By.CSS_SELECTOR, const.Selector.UNRETWEET_CONFIRM
            ).click()
        except (NoSuchElementException, ElementNotInteractableException):
            print(f"failed to unretweet a tweet {self.id=}")
        self.driver.implicitly_wait(0)

    def update(self) -> None:
        self.__init__(self.__element)
