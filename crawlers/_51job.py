from crawlers.baseCrawler import BaseCrawler
from models import Job, Company
import datetime
from resources._51job import *
from crawlers.utils import *
import re


class _51JobCrawler(BaseCrawler):
    base_url = 'https://search.51job.com/list/city,000000,0000,00,9,salary_degree,' \
               'job_name,2,{page}.html?' \
               'lang=c&workyear=work_year&cotype=company_nature&degreefrom=education&' \
               'companysize=scale'

    def __init__(self, task):
        super().__init__(task)
        self.base_url = self.base_url.replace('job_name', task.jobName)
        self.current_page = 1

    def start(self):
        self.init_url()
        url = self.base_url.format(page=self.current_page)
        res = self.send_requests(url)
        document = get_document(res.text)
        self.extract_info_from_document(document)
        total_page = self.get_total_page_by_document(document)
        total_page = int(total_page) if total_page else 1
        self.current_page += 1
        while self.current_page <= total_page:
            res = self.send_requests(self.base_url.format(page=self.current_page))
            document = get_document(res.text)
            self.extract_info_from_document(document)
            self.current_page += 1

    def extract_info_from_document(self, document):
        for item in document.xpath('.//div[@id="resultList"]/div[@class="el"]'):
            job_id = get_simple_dom(item, './/input[@name="delivery_jobid"]/@value')
            try:
                Job.get(Job.uniqueId == job_id)
                continue
            except Job.DoesNotExist:
                pass
            job_url = get_simple_dom(item, './/p[contains(@class, "t1")]/span/a/@href')
            company_url = get_simple_dom(item, './/span[contains(@class, "t2")]/a/@href')
            company_unique_id = self.get_company_unique_id(company_url)
            if not company_unique_id:
                continue
            try:
                company = Company.get(Company.uniqueId == company_unique_id)
                company_id = company.id
            except Company.DoesNotExist:
                company_name = get_simple_dom(item, './/span[@class="t2"]/a/@title')
                position = get_simple_dom(item, './/span[@class="t3"]/text()')
                try:
                    company_id = self.extract_company_info(company_url, company_name, position)
                except:
                    print('Company解析error，companyURL为' + company_url)
                    continue
            try:
                self.extract_job_info(job_url, job_id, company_id)
            except Exception as e:
                # import traceback
                # traceback.print_exc(e)
                # import ipdb;ipdb.set_trace()
                print('Job解析error，jobURL为' + job_url)

    def get_total_page_by_document(self, document):
        page_text = get_simple_dom(document, './/div[@class="p_in"]/span[@class="td"]/text()')
        if page_text:
            return self.get_total_page_by_html(page_text)
        return None

    @staticmethod
    def get_total_page_by_html(html):
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
                if work_year <= int(year):
                    self.base_url = self.base_url.replace('work_year', code)
                    return
            # '05'表示10年以上工作经验
            self.base_url = self.base_url.replace('work_year', '05')
        else:
            # '01'表示不限定工作经验
            self.base_url = self.base_url.replace('work_year', '99')

    def init_city(self):
        if self.task.city:
            for city, code in city_codes.items():
                if self.task.city == city:
                    self.base_url = self.base_url.replace('city', code)
                    return
        # '000000'表示不限定城市
        self.base_url = self.base_url.replace('city', '000000')

    def init_salary(self):
        if self.task.minSalary or self.task.maxSalary:
            min_salary = int(self.task.minSalary or self.task.maxSalary)
            for salary, code in salary_code.items():
                if min_salary < int(salary):
                    self.base_url = self.base_url.replace('salary_degree', code)
                    return
            # '12'表示月薪大于50000
            self.base_url = self.base_url.replace('salary_degree', '12')
        else:
            # '99'表示不限定工资范围
            self.base_url = self.base_url.replace('salary_degree', '99')

    def init_company_nature(self):
        if self.task.companyNature:
            for company_nature, code in nature_code.items():
                if self.task.companyNature == company_nature:
                    self.base_url = self.base_url.replace('company_nature', code)
                    return
        # '99'表示不限定公司性质
        self.base_url = self.base_url.replace('company_nature', '99')

    def init_education(self):
        if self.task.education:
            for education, code in education_code.items():
                if self.task.education in education:
                    self.base_url = self.base_url.replace('education', code)
                    return
        # '99'表示对学历没有要求
        self.base_url = self.base_url.replace('education', '99')

    def init_scale(self):
        if self.task.companyScale:
            company_scale = int(self.task.companyScale)
            for scale, code in scale_code.items():
                if company_scale < int(scale):
                    self.base_url = self.base_url.replace('scale', code)
                    return
            # '07'表示公司规模大于10000人
            self.base_url = self.base_url.replace('scale', '07')
        else:
            # '99'表示不限定公司规模
            self.base_url = self.base_url.replace('scale', '99')

    @staticmethod
    def get_company_unique_id(company_url):
        if not company_url:
            return None
        raw_unique = re.findall('/.*?(\d+).html', company_url)
        return raw_unique[0] if raw_unique else None

    def extract_company_info(self, company_url, company_name, position):
        if not company_url:
            return
        res = self.send_requests(company_url)
        document = get_document(res.text)
        name = get_simple_dom(document, './/div[@class="tHeader tHCop"]/div[contains(@class, "in")]/h1/@title')
        # 使用前程无忧搭建自己公司门户的公司
        if not name:
            return Company.insert(name=company_name,
                                  uniqueId=self.get_company_unique_id(company_url),
                                  position=position,
                                  companyUrl=company_url).execute()
        # 普通公司
        base_info = get_simple_dom(document, './/p[@class="ltype"]/text()', '')
        infos = base_info.split('|')
        nature = infos[0].strip() if len(infos) > 0 else ''
        scale = infos[1].strip() if len(infos) > 1 else ''
        category = infos[2].strip() if len(infos) > 2 else ''
        position_info = get_richtext(document, './/div[@class="inbox"]/p[@class="fp"]')
        position_info = position_info.strip().replace('公司地址：', '')
        position = re.sub('(\(邮编：.*\))', '', position_info) or ''
        position = position.strip()
        description = get_richtext(document, './/div[@class="con_txt"]')
        return Company.insert(name=name,
                              nature=nature,
                              scale=scale,
                              category=category,
                              position=position,
                              description=description,
                              uniqueId=self.get_company_unique_id(company_url),
                              companyUrl=company_url).execute()

    def extract_job_info(self, job_url, job_id, company_id):
        if not job_url:
            return
        res = self.send_requests(job_url)
        if '很抱歉，你选择的职位目前已经暂停招聘' in res.text:
            return
        document = get_document(res.text)
        info_dom = get_simple_dom(document, './/div[@class="tHeader tHjob"]/div/div[@class="cn"]')
        name = get_simple_dom(info_dom, './/h1/@title', '')
        city = get_simple_dom(info_dom, './/span[@class="lname"]/text()', '')
        area = ''
        if '-' in city:
            city_info = city.split('-')
            city = city_info[0]
            area = city_info[1]
        salary_info = get_simple_dom(info_dom, './/strong/text()', '')
        min_salary = max_salary = None
        if '-' in salary_info:
            salary = re.match('(.*)-(.*)(万|元|千)', salary_info)
            if '万' in salary_info:
                min_salary = float(salary[1]) * 10000
                max_salary = float(salary[2]) * 10000
            elif '千' in salary_info:
                min_salary = float(salary[1]) * 1000
                max_salary = float(salary[2]) * 1000
            else:
                min_salary = float(salary[1])
                max_salary = float(salary[2])
            if '/年' in salary_info:
                min_salary = min_salary / 12.0
                max_salary = max_salary / 12.0
        else:
            salary = re.findall('(.*)(万|元|千)', salary_info)
            if salary and len(salary) > 0:
                if '万' in salary_info:
                    min_salary = float(salary[0][0]) * 10000
                elif '千' in salary_info:
                    min_salary = float(salary[0][0]) * 1000
                else:
                    min_salary = float(salary[0][0])
                if '/年' in salary_info:
                    min_salary = min_salary / 12.0
        work_year = education = major = ''
        head_count = None
        publish_date = None
        tags = get_simple_dom(document, './/div[@class="jtag inbox"]/div[@class="t1"]')
        for item in tags.xpath('.//span'):
            tag_class = get_simple_dom(item, './/em/@class')
            tag_value = get_richtext_dom(item).strip()
            if tag_class == 'i1':
                work_year = tag_value.replace('经验', '') if '无工作经验' != tag_value else tag_value
            if tag_class == 'i2':
                education = tag_value
            if tag_class == 'i3':
                counts = re.findall('招(\d+)人', tag_value)
                head_count = counts[0] if counts else None
            if tag_class == 'i4':
                publish_date = '2018-' + tag_value.replace('发布', '')
                publish_date = datetime.datetime.strptime(publish_date, "%Y-%m-%d")
            if tag_class == 'i6':
                major = tag_value
        tag = [_ for _ in tags.xpath('.//div[@class="jtag inbox"]/p[@class="t2"]/span/text()')]
        tag = ' '.join(tag)
        description = get_richtext(document, './/div[@class="bmsg job_msg inbox"]')
        position_info = get_richtext(document, './/div[@class="bmsg inbox"]/p[@class="fp"]') or ''
        position = position_info.replace('上班地址：', '').strip()
        Job.insert(companyId=company_id,
                   name=name,
                   city=city,
                   minSalary=min_salary,
                   maxSalary=max_salary,
                   workYear=work_year,
                   education=education,
                   headCount=head_count,
                   publishDate=publish_date,
                   major=major,
                   tag=tag,
                   description=description,
                   position=position,
                   uniqueId=job_id,
                   jobUrl=job_url,
                   area=area).execute()
