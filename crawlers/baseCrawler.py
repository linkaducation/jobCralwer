class BaseCrawler(object):
    task = None

    def __init__(self, task):
        self.task = task

    def get_total_page_by_document(self, document):
        """
        根据传入放入document获取total_page
        :param document:
        :return:
        """
        raise NotImplementedError

    def get_total_page_by_html(self, html):
        """
        根据传入的html获取total_page
        :param html:
        :return:
        """
        raise NotImplementedError

    def start(self):
        """
        爬虫开始
        :return:
        """
        raise NotImplementedError
