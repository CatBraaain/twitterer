import pickle
import re
from dataclasses import dataclass, field
from typing import List

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from snoop import pp, snoop

from .const import *


class Tweet:
    def __init__(self, element):
        html = element.get_attribute("outerHTML")
        soup = BeautifulSoup(html, "lxml")

        self.__element = element
        self.html = html
        self.__soup = soup

        try:
            self.url = "https://twitter.com" + (
                soup.select_one(Selector.URL).get("href")
            )
        except:
            self.url = "https://twitter.com" + (
                soup.select_one(Selector.ANALYTICS)
                .get("href")
                .removesuffix("/analytics")
            )
        self.id = self.url.split("/")[-1]

        try:
            self.date_time = soup.select_one(Selector.DATE_TIME).get("datetime")
        except:
            self.date_time = ""
        self.is_ad = False if self.date_time else True

        user_elements = soup.select(Selector.USER_ELEMENTS)
        self.user = User(
            name=user_elements[0].text,
            id=user_elements[1].text.removeprefix("@"),
            verified=bool(soup.select(Selector.VERIFIED)),
        )

        content_elements = soup.select(Selector.CONTENT)
        extractor_map = {"span": (lambda e: e.text), "img": (lambda e: e.get("alt"))}
        self.content = "".join([extractor_map[e.name](e) for e in content_elements])

        try:
            analytics = re.sub(
                "[^\\d]", "", soup.select_one(Selector.ANALYTICS).get("aria-label")
            )
        except:
            analytics = ""

        self.stat = Stat(
            replys=re.sub(
                "[^\\d]", "", soup.select_one(Selector.REPLYS).get("aria-label")
            ),
            retweets=re.sub(
                "[^\\d]", "", soup.select_one(Selector.RETWEETS).get("aria-label")
            ),
            likes=re.sub(
                "[^\\d]", "", soup.select_one(Selector.LIKES).get("aria-label")
            ),
            analytics=analytics,
            bookmarks=re.sub(
                "[^\\d]", "", soup.select_one(Selector.BOOKMARKS).get("aria-label")
            ),
        )

        self.media = Media(
            img=Img(
                count=len(soup.select(Selector.IMGS)),
                urls=[e.get("src") for e in soup.select(Selector.IMGS)],
            ),
            video=Video(
                count=len(soup.select(Selector.VIDEOS)),
                thumbnails=[
                    e.get("poster") for e in soup.select(Selector.VIDEO_THUMBNAILS)
                ],
            ),
        )

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_Tweet__element"]
        del state["html"]
        del state["_Tweet__soup"]

        return state


@dataclass
class User:
    name: str
    id: str
    verified: bool


@dataclass
class Stat:
    replys: int
    retweets: int
    likes: int
    analytics: int
    bookmarks: int


class Media:
    def __init__(self, img, video):
        self.has_img = bool(img.count)
        self.img = img
        self.has_video = bool(video.count)
        self.video = video


@dataclass
class Img:
    count: int
    urls: List[str]


@dataclass
class Video:
    count: int
    thumbnails: List[str]
