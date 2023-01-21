import os
from abc import ABC, abstractmethod


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class IProcess(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass


class IFilter(IProcess):
    def __init__(self, id_list):
        self.id_list, self.result = id_list, []
        if len(self.id_list) == 0:
            return
        print(colour_str(f'Filtering[{len(self.id_list)}]: ', form=1, code=31), end='')
        self.result = self.filter_ids()

    @abstractmethod
    def filter_ids(self):
        pass


class IParse(IProcess):
    def __init__(self, id_list):
        self.id_list, self.result = id_list, []
        if len(self.id_list) == 0:
            return
        self.result = self.parse_ids()
        print(colour_str(f'Parsing[{len(self.id_list)}]: ', form=1, code=31)+
              colour_str(f'[finish]', form=1, code=32))

    @abstractmethod
    def parse_ids(self):
        pass


class IStore(IProcess):
    def __init__(self, download_infos, file_name):
        self.download_infos, self.file_name = download_infos, file_name
        if len(self.download_infos) == 0:
            return
        if not os.path.exists(f'./{self.file_name}'):
            os.makedirs(f'./{self.file_name}')
        self.store()
        print(colour_str(f'Storing:{self.file_name}: ', form=1, code=31)+
              colour_str(f'[finish]', form=1, code=32))


    @abstractmethod
    def store(self):
        pass
