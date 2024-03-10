import os
import pickle

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from const import *


class Authenticator:
    def __init__(self, driver):
        self.driver = driver

    def authenticate(self):
        self.driver.get(TWITTER_HOME_URL)

        has_cookie = os.path.exists(COOKIES_PATH)
        if has_cookie:
            self._load_cookies()
            self.driver.get(TWITTER_HOME_URL)

        is_logined = self._wait_for_login
        if not (is_logined):
            self._login()
            self._save_cookies()

    def _load_cookies(self):
        cookies = pickle.load(open(COOKIES_PATH, "rb"))
        for c in cookies:
            self.driver.add_cookie(c)

    def _save_cookies(self):
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(COOKIES_PATH, "wb"), pickle.HIGHEST_PROTOCOL)

    def _wait_for_login(self):
        WebDriverWait(self.driver, 10).until(
            EC.any_of(
                EC.all_of(
                    EC.url_contains(TWITTER_HOME_URL),
                    EC.presence_of_element_located(Selector.LOGIN_SUCCESSED),
                ),
                EC.presence_of_element_located(Selector.LOGIN_FAILED),
            )
        )
        is_logined = bool(self.driver.find_elements(Selector.LOGIN_SUCCESSED))
        return is_logined

    def _login(self):
        self.driver.implicitly_wait(10)

        username_input = self.driver.find_element(By.CSS_SELECTOR, Selector.USERNAME)
        username_input.send_keys(TWITTER_USERNAME, Keys.RETURN)

        password_input = self.driver.find_element(By.CSS_SELECTOR, Selector.PASSWORD)
        password_input.send_keys(TWITTER_PASSWORD, Keys.RETURN)

        self.driver.implicitly_wait(0)

        is_logined = self._wait_for_login()
        if not (is_logined):
            # login failed
            raise Exception
