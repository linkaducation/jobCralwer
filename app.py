from flask import Flask, request
from crawlers.__init__ import run_crawler
from models import Task

app = Flask(__name__)


@app.route('/', methods=['POST'])
def start_crawler_job():
    task = get_task()
    run_crawler(task)


def get_task():
    task_id = request.form['task_id']
    try:
        return Task.get(id=task_id)
    except Task.DoesNotExist:
        return None


if __name__ == '__main__':
    app.run(port=80)
