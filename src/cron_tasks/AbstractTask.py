from abc import ABC


class CronTask(ABC):
    def run_task(self, config):
        pass
