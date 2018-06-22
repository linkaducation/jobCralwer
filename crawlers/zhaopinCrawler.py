from crawlers.baseCrawler import BaseCrawler


class ZhaopinCrawler(BaseCrawler):
    base_url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?jl=city&kw=jobName&isfilter=1&p=1' \
               '&sf=minSalary&st=maxSalary&ct=nature&el=education&we=workYear'

    def start(self):
        pass
