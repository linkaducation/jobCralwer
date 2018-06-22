import requests


class BaseCrawler(object):
    base_url = None

    task = None

    def __init__(self, task):
        self.task = task
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 "
                                                   "(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"})

    def start(self):
        """
        爬虫开始
        :return:
        """
        raise NotImplementedError

    def send_requests(self, url, form_data=None):
        """
        发送请求
        :param form_data:
        :param url:
        :return:
        """
        try:
            if form_data:
                res = self.session.post(url=url, data=form_data, timeout=20)
            else:
                res = self.session.get(url=url, timeout=20)
        except:
            return None
        if self.task.site == '51job':
            res.encoding = 'GBK'
        return res
