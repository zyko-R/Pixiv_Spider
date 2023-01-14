import asyncio

from Process.Parser import *
from Process.Pipeline import *
import threading


class Download(threading.Thread):
    def __init__(self, file_name, id_list, state):
        super().__init__()
        self.file_name = file_name
        self.id_list = id_list
        self.state = state

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        match self.state:
            case 'IMG':
                result = PackageIMG(self.id_list).Result
                WriteIMG(self.file_name, result)
            case 'GIF':
                result = PackageGIF(self.id_list).Result
                WriteGIF(self.file_name, result)


class Prototype:
    def __init__(self, plugin_package):
        file_name, self.id_list = plugin_package.run()
        self.r18_file_name = f'[R18]{file_name}'
        self.nor_file_name = f'[NOR]{file_name}'
        self.run()
        self.end()

    def end(self):
        if os.path.exists(f'./{self.r18_file_name}'):
            Zip(self.r18_file_name, Zip.zip)
            shutil.rmtree(f'./{self.r18_file_name}')
        if os.path.exists(f'./{self.nor_file_name}'):
            Zip(self.nor_file_name, Zip.zip)
            shutil.rmtree(f'./{self.nor_file_name}')

    def run(self):
        ids_nor, ids_r18 = MiddlePackage(self.id_list).Result
        thread_list = [
            Download(self.nor_file_name, ids_nor['img'], 'IMG'),
            Download(self.r18_file_name, ids_r18['img'], 'IMG'),
            Download(self.nor_file_name, ids_nor['gif'], 'GIF'),
            Download(self.r18_file_name, ids_r18['gif'], 'GIF')
        ]
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
