import pickle
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from snoop import pp, snoop

from const import *


class Tweet:
    def __init__(self, element):
        html = element.get_attribute("outerHTML")
        soup = BeautifulSoup(html, "lxml")

        self.__element = element
        self.html = html
        self.__soup = soup

        self.url = "https://twitter.com" + (
            soup.select_one(Selector.ANALYTICS).get("href").removesuffix("/analytics")
        )
        self.tweet_id = self.url.split("/")[-1]

        user_elements = soup.select(Selector.USER_ELEMENTS)
        self.user_name = user_elements[0].text
        self.user_id = user_elements[1].text.removeprefix("@")

        self.verified = bool(soup.select(Selector.VERIFIED))

        try:
            self.date_time = soup.select_one(Selector.DATE_TIME).get("datetime")
        except:
            self.date_time = ""
        self.is_ad = False if self.date_time else True

        content_elements = soup.select(Selector.CONTENT)
        extractor_map = {"span": (lambda e: e.text), "img": (lambda e: e.get("alt"))}
        self.content = "".join([extractor_map[e.name](e) for e in content_elements])

        self.replys = re.sub(
            "[^\\d]", "", soup.select_one(Selector.REPLYS).get("aria-label")
        )
        self.retweets = re.sub(
            "[^\\d]", "", soup.select_one(Selector.RETWEETS).get("aria-label")
        )
        self.likes = re.sub(
            "[^\\d]", "", soup.select_one(Selector.LIKES).get("aria-label")
        )
        self.analytics = re.sub(
            "[^\\d]", "", soup.select_one(Selector.ANALYTICS).get("aria-label")
        )

        self.img_urls = [e.get("src") for e in soup.select(Selector.IMGS)]
        # self.img_cnt = len(self.img_urls)
        # self.has_img = bool(self.img_cnt)

        self.video_cnt = len(soup.select(Selector.VIDEOS))
        # self.has_video = bool(self.video_cnt)
