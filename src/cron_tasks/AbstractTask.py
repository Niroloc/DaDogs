from abc import ABC


class CronTask(ABC):
    task_alias = None
    def __init__(self):
        pass

    def run_task(self):
        pass
