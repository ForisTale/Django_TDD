from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest, TEST_EMAIL, FOR_TEST_EMAIL
from .test_login import SUBJECT
import re


class MyListTest(FunctionalTest):

    def get_url_for_log_in(self, test_email, subject, for_test_email):
        body = self.wait_for_email(test_email, subject, for_test_email)
        url_search = re.search(r"http://.+/.+$", body)
        if not url_search:
            self.fail(f"Could not find url in email body:\n{body}")
        url_for_log_in = url_search.group(0)
        return url_for_log_in

    def log_into_website(self):
        self.browser.find_element_by_name("email").send_keys(TEST_EMAIL)
        self.browser.find_element_by_name("email").send_keys(Keys.ENTER)

        url_for_log_in = self.get_url_for_log_in(TEST_EMAIL, SUBJECT, FOR_TEST_EMAIL)
        self.browser.get(url_for_log_in)

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        # Edith log into website
        self.browser.get(self.live_server_url)
        self.log_into_website()
        self.wait_to_be_logged_in(TEST_EMAIL)

        # She goes to the home page and starts a list
        self.browser.get(self.live_server_url)
        self.add_list_item("Reticulate splines")
        self.add_list_item("Immanentize eschaton")
        first_list_url = self.browser.current_url

        # She notices a "My lists" link, for the first time.
        self.browser.find_element_by_link_text("My lists").click()

        # She sees that her list is in there, named according to its first list item
        self.wait_for(
            lambda: self.browser.find_element_by_link_text("Reticulate splines")
        )
        self.browser.find_element_by_link_text("Reticulate splines").click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )

        # She decides to start another list, just to see
        self.browser.get(self.live_server_url)
        self.add_list_item("Click cows")
        second_list_url = self.browser.current_url

        # Under "My lists", her new list appear
        self.browser.find_element_by_link_text("My lists").click()
        self.wait_for(
            lambda: self.browser.find_element_by_link_text("Click cows")
        )
        self.browser.find_element_by_link_text("Click cows").click()
        self.assertEqual(self.browser.current_url, second_list_url)

        # She log out. The "My lists" option disappears
        self.browser.find_element_by_link_text("Log out").click()
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_elements_by_link_text("My lists"),
                []
            ))
