import shutil
import zipfile
import aiofiles
import os
import aiofiles.os
import imageio
from abc import ABC, abstractmethod
from Main import output, asy_launch


class WriteMixin(ABC):
    pass


class CreWriteMixin(WriteMixin):
    def __init__(self, file_name, download_infos):
        self.download_infos = download_infos
        self.file_name = file_name
        if not os.path.exists(f'./{file_name}'):
            os.makedirs(f'./{file_name}')

        if len(download_infos) > 0:
            output(f'writing in:{self.file_name}: ', form=1, code=31, end='')
            self.write_in()
            output(f'[finish]', form=4, code=32)

    @abstractmethod
    def write_in(self):
        pass


class WriteIMG(CreWriteMixin):
    def write_in(self):
        async def write_in(params):
            img_data, img_name = params[0]
            async with aiofiles.open(f'./{self.file_name}/{img_name}', 'wb+') as f:
                await f.write(img_data)
            output('#', code=33, form=4, end='')

        asy_launch(write_in, (self.download_infos,))


class WriteGIF(CreWriteMixin):
    def write_in(self):
        async def write_in(params):
            gif_bina, delay, gif_name,  = params[0]
            img_path = f'./{self.file_name}/{gif_name}'
            zip_path = f'./{self.file_name}/{gif_name}.zip'
            async with aiofiles.open(zip_path, "wb+") as fp:
                await fp.write(gif_bina)
            await aiofiles.os.mkdir(img_path)
            Zip(img_path, Zip.unzip)
            flames = [imageio.v3.imread(f'{img_path}/{img}') for img in Zip.Name_list]
            imageio.v2.mimsave(f'{img_path}.gif', flames, "GIF", duration=delay)
            shutil.rmtree(img_path)
            os.unlink(f'{zip_path}')
            output('#', code=33, form=4, end='')

        asy_launch(write_in, (self.download_infos,))


class Zip:
    zip = 0
    unzip = 1
    Name_list = []

    def __init__(self, file_name, form):
        self.form = form
        self.zip_path = f'./{file_name}.zip'
        self.unzip_path = f'./{file_name}'
        self.run()

    def run(self):
        match self.form:
            case self.zip: self._zip()
            case self.unzip: self._unzip()

    def _unzip(self):
        with zipfile.ZipFile(self.zip_path, "r") as unzip:
            unzip.extractall(self.unzip_path)
            Zip.Name_list = unzip.namelist()

    def _zip(self):
        with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            Zip.Name_list = z.namelist()
            for item in os.listdir(self.unzip_path):
                z.write(self.unzip_path + os.sep + item)

