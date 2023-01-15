import asyncio
import shutil
import zipfile
import aiofiles
import os
import aiofiles.os
import imageio
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED, as_completed, wait

from Downloader import asy_launch


def output(message, code, form=0, end='\n'):
    print(f'\033[{form};{code}m{message}\033[0m', end=end)


class CreWriteMixin(ABC):
    def __init__(self, file_name, download_infos):
        self.download_infos = download_infos
        self.file_name = file_name

    @abstractmethod
    def write_in(self):
        pass


class WriteIMG(CreWriteMixin):
    def write_in(self):
        async def write_in(img_data, img_name):
            async with aiofiles.open(f'./{self.file_name}/{img_name}', 'wb+') as f:
                await f.write(img_data)
            output('#', code=33, form=4, end='')

        img_bina_list, name_list = self.download_infos
        asy_launch(write_in, (img_bina_list, name_list))


class WriteGIF(CreWriteMixin):
    def write_in(self):
        def load_all_zip(_gif_bina_list, _gif_name_list):
            async def load_zip(_gif_bina, _gif_name):
                zip_path = f'./{self.file_name}/{_gif_name}.zip'
                async with aiofiles.open(zip_path, "wb+") as fp:
                    await fp.write(_gif_bina)
            asy_launch(load_zip, (_gif_bina_list, _gif_name_list))

        def unzip(_gif_name_list):
            _flames_infos = []
            with ThreadPoolExecutor(max_workers=8) as pool:
                task_list = [pool.submit(Zip(f'./{self.file_name}/{_gif_name}').unzip)
                             for _gif_name in _gif_name_list]
                for task in as_completed(task_list):
                    _flames_infos.append(task.result())
            return _flames_infos

        def merge_all(_flames_infos, _delay_list):
            def merge_each(file_path, img_list, _delay):
                flame_paths = [imageio.v3.imread(f'{file_path}/{img}') for img in img_list]
                imageio.v2.mimsave(f'{file_path}.gif', flame_paths, duration=_delay)
                shutil.rmtree(f'{file_path}')
                output('#', code=33, form=4, end='')
            with ThreadPoolExecutor(max_workers=8) as pool:
                task_list = [pool.submit(merge_each, *_flames_infos[i], _delay_list[i])
                             for i in range(0, len(_delay_list))]
                wait(task_list, return_when=ALL_COMPLETED)

        gif_bina_list, delay_list, gif_name_list = self.download_infos
        load_all_zip(gif_bina_list, gif_name_list)
        flames_infos = unzip(gif_name_list)
        merge_all(flames_infos, delay_list)


class Zip:
    def __init__(self, file_path):
        self.zip_path = f'{file_path}.zip'
        self.unzip_path = f'{file_path}'

    def unzip(self):
        with zipfile.ZipFile(self.zip_path, "r") as unzip:
            unzip.extractall(self.unzip_path)
        os.unlink(self.zip_path)
        return self.unzip_path, unzip.namelist()

    def zip(self):
        with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as _zip:
            for item in os.listdir(self.unzip_path):
                _zip.write(self.unzip_path + os.sep + item)
                output('#', code=33, form=4, end='')
        return self.unzip_path, _zip.namelist()

