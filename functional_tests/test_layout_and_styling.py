from functional_tests.base import FunctionalTest
from selenium.webdriver.common.keys import Keys

import time


class LayoutAndStylingTest(FunctionalTest):
    def test_layout_and_styling(self):
        # Edith going to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        input_box = self.get_item_input_box()
        time.sleep(2)
        self.assertAlmostEqual(
            input_box.location["x"] + input_box.size["width"] / 2,
            512,
            delta=10
        )

        # She start a new list and sees the input is nicely centered there too
        self.add_list_item("testing")
        input_box = self.get_item_input_box()
        self.assertAlmostEqual(
            input_box.location["x"] + input_box.size["width"] / 2,
            512,
            delta=10
        )
