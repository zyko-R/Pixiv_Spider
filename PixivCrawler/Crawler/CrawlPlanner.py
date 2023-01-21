from .SemiCrawler.IDHandler import *


class ScheduledScheme:
    @abstractmethod
    def __init__(self, captor):
        self.Scheme = captor

    def enable(self):
        return self.Scheme(IDHandler())


class CrawlPlanner:
    def __init__(self, executor):
        self.Executor = executor

    def enable(self, schedule_scheme):
        crawler = schedule_scheme.enable()
        self.Executor.CrawlerList.append(crawler)

    def regret(self):
        if len(self.Executor.CrawlerList) != 0:
            undo = self.Executor.CrawlerList[-1]
            self.Executor.CrawlerList.pop(-1)
            return undo


class Executor:
    def __init__(self):
        self.CrawlerList = []

    def action(self):
        for crawler in self.CrawlerList:
            crawler.crawl()
