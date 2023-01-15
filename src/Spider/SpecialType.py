from Spider.Component.Prototype import Prototype
from Spider.Component.ExpectID import *


class ByAuthorIDCrawler:
    def __init__(self):
        crawler = Prototype()
        ByAuthorID(crawler).crawl()


class ByArtworkIDCrawler:
    def __init__(self):
        crawler = Prototype()
        ByArtworkID(crawler).crawl()


class ByTraceCrawler:
    def __init__(self):
        crawler = Prototype()
        ByTrace(crawler).crawl()


class BySubCrawler:
    def __init__(self):
        crawler = Prototype()
        BySub(crawler).crawl()


class ByRankingCrawler:
    def __init__(self):
        crawler = Prototype()
        ByRanking(crawler).crawl()
