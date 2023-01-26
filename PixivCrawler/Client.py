import os

from PixivCrawler.Crawler.CrawlPlanner import CrawlPlanner, Executor, By


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class Client:
    def __init__(self):
        self.scheme_list = [
            ('Similar Artworks by artworkID', By.Artwork),
            ('Artworks by author', By.AuthorID),
            ('Artworks by Sub. on pixiv', By.Sub),
            ('Artworks by Ranking ', By.Ranking),
        ]
        while True:
            try:
                global_source_limit = int(input(colour_str('global source limit = ', form=1, code=31)))
                if global_source_limit < 0:
                    raise ValueError
                break
            except ValueError:
                print(colour_str('Type in a positive integer', form=1, code=31))

        self.Planner = CrawlPlanner(Executor(global_source_limit))
        self.menu()

    def menu(self):
        menu_str = f"TYPE\n" +\
                   f"   0 | {colour_str('StartCrawling', form=1, code=32)}\n" +\
                   f"  -1 | {colour_str('Undo', form=1, code=31)}\n"
        for index, scheme in enumerate(self.scheme_list):
            menu_str += f'\n   {index+1} | {colour_str(scheme[0], form=1, code=33)}'
        print(menu_str)

    def run(self):
        def get_key():
            try:
                _key = int(input(colour_str(f'>? ', form=1, code=31)))
            except ValueError:
                print(colour_str('Type in a Integer', form=1, code=31))
                _key = get_key()
            return _key

        def start_crawling():
            self.Planner.Executor.action()
            self.Planner.Executor.CrawlerList.clear()

        def undo_crawl():
            crawler_list = self.Planner.Executor.CrawlerList
            if len(crawler_list) == 0:
                print(colour_str(f'CommandList VOID', form=1, code=31))
            else:
                print(colour_str(f'Undo <{crawler_list[-1]}>', form=1, code=31))
                self.Planner.undo()

        def register(scheme):
            self.Planner.enable(scheme)

        while True:
            key = get_key()
            match key:
                case key if 0 < key <= len(self.scheme_list):
                    register(self.scheme_list[key-1][1])
                case 0: start_crawling()
                case -1: undo_crawl()
                case -2: print(self.Planner.Executor.CrawlerList)
                case _: print(colour_str(f'Unknown Command', form=1, code=31))
