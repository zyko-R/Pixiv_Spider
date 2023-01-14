import asyncio
import threading
import time

from Process.Parser import *
from Process.Pipeline import *


class Prototype:
    def __init__(self, plugin_package):
        file_name, self.id_list = plugin_package.run()
        self.r18_file_name = f'[R18]{file_name}'
        self.nor_file_name = f'[NOR]{file_name}'
        self.craw()
        self.end()

    def end(self):
        if os.path.exists(f'./{self.r18_file_name}'):
            Zip(f'./{self.r18_file_name}').zip()
            shutil.rmtree(f'./{self.r18_file_name}')
        if os.path.exists(f'./{self.nor_file_name}'):
            Zip(f'./{self.nor_file_name}').zip()
            shutil.rmtree(f'./{self.nor_file_name}')

    def craw(self):
        ids_nor, ids_r18 = MiddlePackage(self.id_list).Result

        class Download(threading.Thread):
            def __init__(self, file_name, id_list):
                super().__init__()
                self.file_name, self.id_list = file_name, id_list

        class DownloadIMG(Download):
            def run(self):
                asyncio.set_event_loop(asyncio.new_event_loop())
                result = PackageIMG(self.id_list).Result
                WriteIMG(self.file_name, result)

        class DownloadGIF(Download):
            def run(self):
                asyncio.set_event_loop(asyncio.new_event_loop())
                result = PackageGIF(self.id_list).Result
                WriteGIF(self.file_name, result)

        task_list = [
            DownloadIMG(self.nor_file_name, ids_nor['img']),
            DownloadIMG(self.r18_file_name, ids_r18['img']),
            DownloadGIF(self.nor_file_name, ids_nor['gif']),
            DownloadGIF(self.r18_file_name, ids_r18['gif'])
        ]
        for task in task_list:
            task.start()
        for task in task_list:
            task.join()
