from typing import List

from bs4 import BeautifulSoup, Tag


class CustomSoup(BeautifulSoup):
    def find_element_attr(self, locator: str, key: str) -> str:
        element = self.select_one(locator)
        if element is None:
            return ""
        return self.get_element_attr(element, key)

    def find_elements_attr(self, locator: str, key: str) -> List[str]:
        elements = self.select(locator)
        return [self.get_element_attr(element, key) for element in elements]

    def get_element_attr(self, element: Tag | None, key: str) -> str:
        if element is None:
            return ""
        value = element.get(key)
        if isinstance(value, str):
            return value
        elif isinstance(value, list):  # class values
            return " ".join(value)
        else:
            return ""

    def get_element_text(self, element: Tag | None) -> str:
        if element is None:
            return ""
        return element.text
