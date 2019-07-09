from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.conf import settings

from .server_tools import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session
from .server_tools import reset_database

from datetime import datetime
import os
import time
import poplib

MAX_WAIT = 20
TEST_EMAIL = "staging_test_email@yahoo.com"
FOR_TEST_EMAIL = "staging_test_email"
SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "screendumps"
)
SUBJECT = "Your login link for Superlists."


def wait(fn):

    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException, IndexError) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                else:
                    time.sleep(0.1)
    return modified_fn


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.staging_server = os.environ.get("STAGING_SERVER")
        if self.staging_server:
            self.live_server_url = "http://" + self.staging_server
            reset_database(self.staging_server)

    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.browser.window_handles):
                self._windowid = ix
                # noinspection PyDeprecation
                self.browser.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()
        self.browser.quit()
        super().tearDown()

    def _test_has_failed(self):
        return any(error for (method, error) in self._outcome.errors)

    def take_screenshot(self):
        filename = self._get_filename() + ".png"
        print("screenshotting to", filename)
        self.browser.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + ".html"
        print("dumping page HTML to", filename)
        with open(filename, "w") as f:
            f.write(self.browser.page_source)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(":", ".")[:19]
        return "{folder}/{classname}.{method}-window-{windowid}-{timestamp}".format(
            folder=SCREEN_DUMP_LOCATION,
            classname=self.__class__.__name__,
            method=self._testMethodName,
            windowid=self._windowid,
            timestamp=timestamp
        )

    def get_item_input_box(self):
        return self.browser.find_element_by_id("id_text")

    def add_list_item(self, item_text):
        num_rows = len(self.browser.find_elements_by_css_selector("#id_list_table tr"))
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        item_number = num_rows + 1
        self.wait_for_row_in_list_table(f"{item_number}: {item_text}")

    @wait
    def wait_for(self, fn):
        return fn()

    @wait
    def wait_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id("id_list_table")
        rows = table.find_elements_by_tag_name("tr")
        self.assertIn(row_text, [row.text for row in rows])

    @wait
    def wait_to_be_logged_in(self, email):
        self.browser.find_element_by_link_text("Log out")
        navbar = self.browser.find_element_by_css_selector(".navbar")
        self.assertIn(email, navbar.text)

    @wait
    def wait_to_be_logged_out(self, email):
        self.browser.find_element_by_name("email")
        navbar = self.browser.find_element_by_css_selector(".navbar")
        self.assertNotIn(email, navbar.text)

    def wait_for_email(self, test_email, subject, for_test_email):

        if not self.staging_server:
            return self.wait_for_mock_email_body(test_email, subject)

        start = time.time()
        while time.time() - start < 60:
            email_id = None
            inbox = poplib.POP3_SSL("pop.mail.yahoo.com")
            try:
                inbox.user(test_email)
                inbox.pass_(for_test_email)
                # get 10 newest messages
                count, _ = inbox.stat()
                for i in reversed(range(max(1, count - 10), count + 1)):
                    print("getting msg", i)
                    _, lines, __ = inbox.retr(i)
                    lines = [l.decode("utf-8") for l in lines]
                    if f"Subject: {subject}" in lines:
                        email_id = i
                        body = "\n".join(lines)
                        return body
                time.sleep(1)
            finally:
                if email_id:
                    inbox.dele(email_id)
                inbox.quit()

    @wait
    def wait_for_mock_email_body(self, test_email, subject):
        email = mail.outbox[0]
        self.assertIn(test_email, email.to)
        self.assertEqual(email.subject, subject)
        return email.body

    def create_pre_authenticated_session(self, email):
        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, email)

        else:
            session_key = create_pre_authenticated_session(email)

        # to set a cookie we need to first visit the domain.
        # 404 pages load the quickest!
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
        ))
