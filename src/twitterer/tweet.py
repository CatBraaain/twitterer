from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from . import const
from .customsoup import CustomSoup


@dataclass
class User:
    name: str
    id: str
    verified: bool


@dataclass
class Stats:
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
class Media:
    img_count: int
    img_urls: list[str]
    video_count: int
    video_thumbnails: list[str]


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
    stats: Stats
    status: Status
    media: Media

    def __init__(self, driver: WebDriver, element: WebElement) -> None:
        self.driver = driver
        self.parse_element(element)

    def parse_element(self, element: WebElement) -> None:
        html = element.get_attribute("outerHTML")
        if html is None:
            raise TypeError
        soup = CustomSoup(html, "lxml")

        self.__element = element
        self.html = html
        self.__soup = soup

        url_href = soup.find_element_str(const.Selector.URL, "href")
        analytics_href = soup.find_element_str(const.Selector.ANALYTICS, "href")
        url_path = url_href or analytics_href.removesuffix("/analytics")
        self.url = "https://x.com" + url_path

        self.id = self.url.split("/")[-1]

        self.date_time = soup.find_element_str(const.Selector.DATE_TIME, "datetime")
        self.is_ad = not bool(self.date_time)

        user_element = soup.select_one(const.Selector.USER_ELEMENT)
        self.user = User(
            name=soup.get_element_text(user_element),
            id=soup.get_element_str(user_element, "href").removeprefix("/"),
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

        replys = soup.find_element_num(const.Selector.REPLYS, "aria-label")
        retweets = soup.find_element_num(const.Selector.RETWEETS, "aria-label")
        likes = soup.find_element_num(const.Selector.LIKES, "aria-label")
        analytics = soup.find_element_num(const.Selector.ANALYTICS, "aria-label")
        bookmarks = soup.find_element_num(const.Selector.BOOKMARKS, "aria-label")

        self.stats = Stats(
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
            img_count=len(soup.select(const.Selector.IMGS)),
            img_urls=soup.find_elements_str(const.Selector.IMGS, "src"),
            video_count=len(soup.select(const.Selector.VIDEOS)),
            video_thumbnails=thumbnails,
        )

    def __getstate__(self) -> dict[str, Any]:
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
        self.parse_element(self.__element)
