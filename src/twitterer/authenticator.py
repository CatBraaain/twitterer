import os
import pickle

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .const import *


class Authenticator:

    def __init__(self, driver):
        self.driver = driver
        self.condition_logined = EC.all_of(
            EC.url_contains(TWITTER_HOME_URL),
            EC.presence_of_element_located((By.CSS_SELECTOR, Selector.LOGIN_SUCCESSED)),
        )
        self.condition_required_to_login = EC.all_of(
            EC.url_contains(TWITTER_LOGIN_URL),
            EC.presence_of_element_located((By.CSS_SELECTOR, Selector.LOGIN_FAILED)),
        )

    def authenticate(self):
        self.driver.get(TWITTER_HOME_URL)

        has_cookie = os.path.exists(COOKIES_PATH)
        if has_cookie:
            try:
                self._load_cookies()
            except:
                pass
            self.driver.get(TWITTER_HOME_URL)

        is_logined = self._determine_logined()
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

    def _determine_logined(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.any_of(
                    self.condition_logined,
                    self.condition_required_to_login,
                )
            )
            return bool(self.condition_logined(self.driver))
        except:
            return False

    def _login(self):
        try:
            self.driver.implicitly_wait(10)

            username_input = self.driver.find_element(
                By.CSS_SELECTOR, Selector.USERNAME
            )
            username_input.send_keys(TWITTER_USERNAME, Keys.RETURN)

            password_input = self.driver.find_element(
                By.CSS_SELECTOR, Selector.PASSWORD
            )
            password_input.send_keys(TWITTER_PASSWORD, Keys.RETURN)

            self.driver.implicitly_wait(0)

            WebDriverWait(self.driver, 10).until(self.condition_logined)
        except:
            raise Exception("login failed")
