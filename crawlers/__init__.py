from crawlers import _51job
from models import Task
import datetime

crawlers = {
    '51job': _51job._51JobCrawler
}


def run_crawler(task):
    crawler = crawlers.get(task.site)(task)
    crawler.start()
    Task.update(finished=True,
                finishedDate=datetime.datetime.now()
                ).where(Task.id == task.id).execute()
