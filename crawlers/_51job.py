from crawlers.baseCrawler import BaseCrawler
from models import Job, Company
from resources._51job import *
from crawlers.utils import *
import re


class _51JobCrawler(BaseCrawler):
    base_url = 'https://search.51job.com/list/{city},000000,0000,00,9,{salary_degree},' \
               '%25E4%25BA%25BA%25E5%258A%259B%25E8%25B5%2584%25E6%25BA%2590,2,{page}.html?' \
               'lang=c&workyear={work_year}&cotype={company_nature}&degreefrom={education}&' \
               'companysize={scale}'

    def __init__(self, task):
        super().__init__(task)
        self.current_page = 1

    def start(self):
        self.init_url()
        url = self.base_url.format(page=self.current_page)
        res = self.send_requests(url)
        document = get_document(res.text)

        total_page = self.get_total_page_by_document(document)

    def extract_info_from_document(self, document):
        for item in document.xpath('.//div[@id="resultList"]/div[@class="el"]'):
            job_id = get_simple_dom(item, './/input[@name="delivery_jobid"]/@value')
            try:
                job = Job.get(Job.uniqueId == job_id)
                continue
            except Job.DoesNotExist:
                pass
            job_url = get_simple_dom(item, './/p[@class="t1"]/sapn/a/@href')
            company_url = get_simple_dom(item, './/span[@class="t2"]/a/@href')
            unique_id = self.get_company_unique_id(company_url)
            if not unique_id:
                continue
            try:
                company = Company.get(Company.uniqueId == unique_id)
            except Company.DoesNotExist:
                res = self.send_requests(url=company_url)
                company_id = self.extract_company_info(res)


    def get_total_page_by_document(self, document):
        page_text = get_simple_dom(document, './/div[@class="p_in"]/span[@class="td"]/text()')
        if not page_text:
            return self.get_total_page_by_html(page_text)
        return None

    def get_total_page_by_html(self, html):
        page_info = re.findall('共(\d+)页，到第', html)
        return page_info[0] if page_info else None

    def init_url(self):
        self.init_work_year()
        self.init_city()
        self.init_salary()
        self.init_company_nature()
        self.init_education()
        self.init_scale()

    def init_work_year(self):
        if self.task.workYear:
            work_year = int(self.task.workYear)
            for year, code in work_year_code.items():
                if work_year < int(year):
                    self.base_url.format(work_year=code)
                    return
            # '05'表示10年以上工作经验
            self.base_url.format(work_year='05')
        else:
            # '01'表示不限定工作经验
            self.base_url.format(work_year='01')

    def init_city(self):
        if self.task.city:
            for city, code in city_codes.items():
                if self.task.city == city:
                    self.base_url.format(city=code)
                    return
        # '000000'表示不限定城市
        self.base_url.format(city='000000')

    def init_salary(self):
        if self.task.minSalary or self.task.maxSalary:
            min_salary = int(self.task.minSalary or self.task.maxSalary)
            for salary, code in salary_code.items():
                if min_salary < int(salary):
                    self.base_url.format(salary_degree=code)
                    return
            # '12'表示月薪大于50000
            self.base_url.format(salary_degree='12')
        else:
            # '99'表示不限定工资范围
            self.base_url.format(salary_degree='99')

    def init_company_nature(self):
        if self.task.companyNature:
            for company_nature, code in nature_code.items():
                if self.task.companyNature == company_nature:
                    self.base_url.format(company_nature=code)
                    return
        # '99'表示不限定公司性质
        self.base_url.format(company_nature='99')

    def init_education(self):
        if self.task.education:
            for education, code in education_code.items():
                if self.task.education in education:
                    self.base_url.format(education=code)
                    return
        # '99'表示对学历没有要求
        self.base_url.format(education='99')

    def init_scale(self):
        if self.task.companyScale:
            company_scale = int(self.task.companyScale)
            for scale, code in scale_code.items():
                if company_scale < int(scale):
                    self.base_url.format(scale=code)
                    return
            # '07'表示公司规模大于10000人
            self.base_url.format(scale='07')
        else:
            # '99'表示不限定公司规模
            self.base_url.format(scale='99')

    @staticmethod
    def get_company_unique_id(company_url):
        if not company_url:
            return None
        raw_unique = re.findall('/.*?(\d+).html', company_url)
        return raw_unique[0] if raw_unique else None

    @staticmethod
    def extract_company_info(res):
        document = get_document(res)
        name = get_simple_dom(document, './/div[@class="tHeader tHCop"]/div[@class="in img_on"]/h1/@title')
        if not name:
            return None
