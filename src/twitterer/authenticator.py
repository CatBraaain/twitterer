import os
import pickle
from typing import Callable, List, Literal

from selenium.common.exceptions import (
    InvalidCookieDomainException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from . import const

type type_of_EC_all_of = Callable[[WebDriver], List[object] | Literal[False]]


class Authenticator:
    driver: WebDriver
    condition_logined: type_of_EC_all_of
    condition_required_to_login: type_of_EC_all_of

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.condition_logined = EC.all_of(
            EC.url_contains(const.TWITTER_HOME_URL),
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, const.Selector.LOGIN_SUCCESSED)
            ),
        )
        self.condition_required_to_login = EC.all_of(
            EC.url_contains(const.TWITTER_LOGIN_URL),
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, const.Selector.LOGIN_FAILED)
            ),
        )

    def authenticate(self) -> None:
        self.driver.get(const.TWITTER_LOGIN_URL)

        has_cookie = os.path.exists(const.COOKIES_PATH)
        if has_cookie:
            try:
                self._load_cookies()
            except InvalidCookieDomainException:
                pass
            self.driver.get(const.TWITTER_HOME_URL)

        is_logined = self._is_logined()
        if not (is_logined):
            self._login()
            self._save_cookies()

    def _load_cookies(self) -> None:
        cookies = pickle.load(open(const.COOKIES_PATH, "rb"))
        for c in cookies:
            self.driver.add_cookie(c)

    def _save_cookies(self) -> None:
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(const.COOKIES_PATH, "wb"), pickle.HIGHEST_PROTOCOL)

    def _is_logined(self) -> bool:
        try:
            WebDriverWait(self.driver, 10).until(
                EC.any_of(
                    self.condition_logined,
                    self.condition_required_to_login,
                )
            )
            return bool(self.condition_logined(self.driver))
        except NoSuchElementException:
            return False

    def _login(self) -> None:
        try:
            if const.TWITTER_USERNAME is None or const.TWITTER_PASSWORD is None:
                raise EnvironmentError("username or password is not found")

            self.driver.implicitly_wait(10)

            username_input = self.driver.find_element(
                By.CSS_SELECTOR, const.Selector.USERNAME
            )
            username_input.send_keys(const.TWITTER_USERNAME, Keys.RETURN)

            password_input = self.driver.find_element(
                By.CSS_SELECTOR, const.Selector.PASSWORD
            )
            password_input.send_keys(const.TWITTER_PASSWORD, Keys.RETURN)

            self.driver.implicitly_wait(0)

            WebDriverWait(self.driver, 10).until(self.condition_logined)
        except NoSuchElementException:
            raise Exception("login failed")
