from PixivCrawler.Crawler.SemiCrawler import IDHandler
from PixivCrawler.Crawler.SemiCrawler import IDCaptor


class By:
    AuthorID = IDCaptor.ByAuthorID
    Artwork = IDCaptor.ByArtworkID
    Sub = IDCaptor.BySub
    Ranking = IDCaptor.ByRanking


class CrawlPlanner:
    def __init__(self, executor):
        self.Executor = executor

    def enable(self, captor):
        self.Executor.CrawlerList.append(captor(IDHandler.IDHandler()))

    def undo(self):
        if len(self.Executor.CrawlerList) != 0:
            self.Executor.CrawlerList.pop(-1)


class Executor:
    def __init__(self, source_limit):
        IDCaptor.IDCaptor.source_limit = source_limit
        self.CrawlerList = []

    def action(self):
        for crawler in self.CrawlerList:
            crawler.crawl()
