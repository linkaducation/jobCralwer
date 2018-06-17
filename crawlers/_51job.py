from crawlers.baseCrawler import BaseCrawler
from crawlers.utils import *
import re


class _51JobCrawler(BaseCrawler):

    def start(self):
        pass

    def get_total_page_by_document(self, document):
        page_text = get_simple_dom(document, './/div[@class="p_in"]/span[@class="td"]/text()')
        if not page_text:
            return self.get_total_page_by_html(page_text)
        return None

    def get_total_page_by_html(self, html):
        page_info = re.findall('共(\d+)页，到第', html)
        return page_info[0] if page_info else None
