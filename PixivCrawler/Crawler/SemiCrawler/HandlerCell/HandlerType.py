import asyncio
import os
import threading
from abc import abstractmethod
from PixivCrawler.Crawler.SemiCrawler.HandlerCell.HandlerAPI import IFilterAPI, IParseAPI, IStoreAPI


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class HandlerType(threading.Thread):
    APIClass = None

    def __init__(self, api):
        super().__init__()
        if not isinstance(api, self.APIClass):
            raise ValueError(f'{api} is not belong to {self.APIClass} ')
        self.api, self.result = api, None

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.result = self.handle()
        print(colour_str(f'[NEXT]', form=1, code=37))

    @abstractmethod
    def handle(self):
        pass


class Filter(HandlerType):
    APIClass = IFilterAPI

    def handle(self):
        if isinstance(self.api.id_list, list) and len(self.api.id_list) != 0:
            print(colour_str(f'Filtering<{len(self.api.id_list)}>', form=1, code=34))
            return self.api.filter()


class Parse(HandlerType):
    APIClass = IParseAPI

    def handle(self):
        if isinstance(self.api.id_list, list) and len(self.api.id_list) != 0:
            print(colour_str(f'Parsing<{len(self.api.id_list)}>', form=1, code=34))
            return self.api.parse()


class Store(HandlerType):
    APIClass = IStoreAPI

    def handle(self):
        if isinstance(self.api.infos, (list, tuple)) and len(self.api.infos) != 0:
            if not os.path.exists(f'./{self.api.file_name}'):
                os.makedirs(f'./{self.api.file_name}')
            print(colour_str(f'Storing<{self.api.file_name}>', form=1, code=34,))
            return self.api.store()

