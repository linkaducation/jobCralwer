import re
from models import Company, Job
from crawlers.baseCrawler import BaseCrawler
from resources.Zhaopin import *
from crawlers.utils import *


class ZhaopinCrawler(BaseCrawler):
    base_url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?jl=city&kw=jobName&isfilter=1&p={page}' \
               '&sf=minSalary&st=maxSalary&ct=nature&el=education&we=workYear'

    def __init__(self, task):
        super().__init__(task)
        self.base_url = self.base_url.replace('jobName', task.jobName)
        self.current_page = 1

    def start(self):
        self.init_url()
        url = self.base_url.format(page=self.current_page)
        res = self.send_requests(url)
        document = get_document(res.text)
        self.extract_info_from_document(document)

    def extract_info_from_document(self, document):
        for item in document.xpath('.//div[@id="newlist_list_content_table"]/table[@class="newlist"]'):
            job_url = get_simple_dom(item, './/td[@class="zwmc"]/div/a/@href')
            job_unique_id = self.get_job_id(job_url)
            try:
                Job.get(uniqueId=job_unique_id)
                continue
            except Job.DoesNotExist:
                pass
            company_url = get_simple_dom(item, './/td[@class="gsmc"]/a/@href')
            company_unique_id = self.get_company_unique_id(company_url)
            if not company_unique_id:
                continue
            try:
                company = Company.get(Company.uniqueId == company_unique_id, Company.site == self.task.site)
                company_id = company.id
            except Company.DoesNotExist:
                company_name = get_simple_dom(item, './/td[@class="gsmc"]/a/text()')
                position = get_simple_dom(item, './/td[@class="gzdd"]/text()')
                company_id = self.extract_company_info(company_url, company_name, position)

    def init_url(self):
        self.init_salary()
        self.init_nature()
        self.init_education()
        self.init_work_year()

    def init_salary(self):
        self.base_url = self.base_url.replace('minSalary', self.task.minSalary if self.task.minSalary else '1')
        self.base_url = self.base_url.replace('maxSalary', self.task.maxSalary if self.task.maxSalary else '99999')

    def init_nature(self):
        if self.task.companyNature:
            for nature, code in nature_code.items():
                if self.task.companyNature in nature:
                    self.base_url = self.base_url.replace('nature', code)
                    return
        # '-1'表示公司性质不限
        self.base_url = self.base_url.replace('nature', '-1')

    def init_education(self):
        if self.task.education:
            for education, code in education_code.items():
                if self.task.education in education:
                    self.base_url = self.base_url.replace('education', code)
                    return
        # '-2'表示不限学历
        self.base_url = self.base_url.replace('education', '-2')

    def init_work_year(self):
        if self.task.workYear:
            work_year = self.task.workYear
            for year, code in work_year_code.items():
                if work_year <= year:
                    self.base_url = self.base_url.replace('workYear', code)
                    return
            # '1099'表示10年以上工作经验
            self.base_url = self.base_url.replace('workYear', '1099')
        else:
            # '-1'表示不限定工作经验
            self.base_url = self.base_url.replace('workYear', '-1')

    @staticmethod
    def get_company_unique_id(company_url):
        if not company_url:
            return None
        unique_id = re.findall('.*?(\d+).htm', company_url)
        return unique_id[0] if unique_id else None

    @staticmethod
    def get_job_id(job_url):
        if not job_url:
            return None
        job_id = re.findall('http://jobs.zhaopin.com/(.*).htm', job_url)
        return job_id[0] if job_id else None

    def extract_company_info(self, company_url, company_name, position):
        res = self.send_requests(company_url)
        document = get_document(res.text)
        name = get_simple_dom(document, './/div[@class="mainLeft"]/div/h1/text()', '').strip()
        if not name:
            return Company.insert(site=self.task.site,
                                  name=company_name,
                                  uniqueId=self.get_company_unique_id(company_url),
                                  companyUrl=company_url,
                                  position=position).execute()
        for item in document.xpath('.//table[@class="comTinyDes"]/tbody/tr'):
            td_list = item.xpath('.//td')
            key = get_simple_dom(td_list, './/span/text()')
