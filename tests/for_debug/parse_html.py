import os
import pickle
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from snoop import pp, snoop
from test_helper import *

os.chdir(Path(__file__).parent)
from twitterer.const import *


def main():
    html = file_to_obj()
    soup = BeautifulSoup(html, "lxml")


main()
