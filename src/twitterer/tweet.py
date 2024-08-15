import re
from dataclasses import dataclass
from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag
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
class Media:
    img_count: int
    img_urls: List[str]
    video_count: int
    video_thumbnails: List[str]


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
        self.parse_element(element)

    def parse_element(self, element: WebElement) -> None:
        html = element.get_attribute("outerHTML")
        if html is None:
            raise TypeError
        soup = BeautifulSoup(html, "lxml")

        self.__element = element
        self.html = html
        self.__soup = soup

        url_href = self._get_element_attr(const.Selector.URL, "href")
        analytics_href = self._get_element_attr(const.Selector.ANALYTICS, "href")
        url_path = url_href or analytics_href.removesuffix("/analytics")
        self.url = "https://x.com" + url_path

        self.id = self.url.split("/")[-1]

        self.date_time = self._get_element_attr(const.Selector.DATE_TIME, "datetime")
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

        replys = (
            re.sub(
                "[^\\d]",
                "",
                self._get_element_attr(const.Selector.REPLYS, "aria-label"),
            )
            or "0"
        )
        retweets = (
            re.sub(
                "[^\\d]",
                "",
                self._get_element_attr(const.Selector.RETWEETS, "aria-label"),
            )
            or "0"
        )
        likes = (
            re.sub(
                "[^\\d]", "", self._get_element_attr(const.Selector.LIKES, "aria-label")
            )
            or "0"
        )
        analytics = (
            re.sub(
                "[^\\d]",
                "",
                self._get_element_attr(const.Selector.ANALYTICS, "aria-label"),
            )
            or "0"
        )
        bookmarks = (
            re.sub(
                "[^\\d]",
                "",
                self._get_element_attr(const.Selector.BOOKMARKS, "aria-label"),
            )
            or "0"
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
            img_count=len(soup.select(const.Selector.IMGS)),
            img_urls=self._get_elements_attr(const.Selector.IMGS, "src"),
            video_count=len(soup.select(const.Selector.VIDEOS)),
            video_thumbnails=thumbnails,
        )

    def _get_element_attr(self, locator: str, key: str) -> str:
        element = self.__soup.select_one(locator)
        if element is None:
            return ""
        return self._get_attr_from_element(element, key)

    def _get_elements_attr(self, locator: str, key: str) -> List[str]:
        elements = self.__soup.select(locator)
        return [self._get_attr_from_element(element, key) for element in elements]

    def _get_attr_from_element(self, element: Tag, key: str) -> str:
        value = element.get(key)
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            return ",".join(value)
        elif value is None:
            return ""
        else:
            return ""

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
        self.parse_element(self.__element)
