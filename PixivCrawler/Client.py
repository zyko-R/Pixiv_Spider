import os

from PixivCrawler.Crawler.CrawlPlanner import ScheduledScheme, CrawlPlanner, Executor
from PixivCrawler.Crawler.SemiCrawler.IDCaptor import ByArtworkID, ByAuthorID, BySub, ByRanking


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class Client:
    def __init__(self):
        class MenuComponent:
            def __init__(self, context, scheme):
                self.context, self.scheme = context, scheme

            def __repr__(self):
                return self.scheme
        self.Planner = CrawlPlanner(Executor())
        self.scheme_list = [
            MenuComponent('Similar Artworks by artworkID', scheme=ScheduledScheme(ByArtworkID)),
            MenuComponent('Artworks by author', scheme=ScheduledScheme(ByAuthorID)),
            MenuComponent('Artworks by Sub. on pixiv', scheme=ScheduledScheme(BySub)),
            MenuComponent('Artworks by Ranking ', scheme=ScheduledScheme(ByRanking)),
        ]

    def menu(self):
        menu_str = f" TYPE\n" +\
                   f"   0 | {colour_str('StartCrawling', form=1, code=32)}\n" +\
                   f"  -1 | {colour_str('Undo', form=1, code=31)}\n"
        for index, scheme in enumerate(self.scheme_list):
            menu_str += f'\n   {index+1} | {colour_str(scheme.context, form=1, code=33)}'
        print(menu_str)

    def run(self):
        self.menu()
        while True:
            key = int(input(colour_str(f'>? ', form=1, code=31)))
            if key > 0 & key <= len(self.scheme_list):
                self.Planner.enable(self.scheme_list[key-1].scheme)
            match key:
                case  0: self.Planner.Executor.action()
                case -1: print(colour_str(f'Undo <{self.Planner.regret()}>', form=1, code=31))
