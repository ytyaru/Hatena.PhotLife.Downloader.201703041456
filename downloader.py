#!python3
#encoding:utf-8
import dataset
import requests
import time
class Downloader(object):
    def __init__(self, hatena_id, path_hatena_photolife_sqlite3):
        self.hatena_id = hatena_id
        self.path_hatena_photolife_sqlite3 = path_hatena_photolife_sqlite3
        self.db_photo = dataset.connect('sqlite:///' + path_hatena_photolife_sqlite3)
        
    def downloads(self):
       for record in self.db_photo['Contents'].find(Content=None):
            if (None == record['Content']):
                url = self.__create_url(record['ItemId'], record['FileExtension'])
                image = self.__get_image(url)
                self.__update_image(record, image)
        
    def __create_url(self, item_id, ext):
        print(item_id)
        url = "http://cdn-ak.f.st-hatena.com/images/fotolife/{0}/{1}/{2}/{3}.{4}".format(
                self.hatena_id[0:1], 
                self.hatena_id,
                item_id[:-6],
                item_id,
                ext)
        print(url)
        return url

    def __get_image(self, url):
        time.sleep(3)
        res = requests.get(url)
        print(res.headers)
        if 'image' not in res.headers['Content-Type']:
            print('imageデータではありません。')
            return
        print(res.headers['Content-Length'])
        print(res.raw)
        print(res.content)
        return res.content

    def __update_image(self, record, image):
        data = dict(ItemId=record['ItemId'], FileExtension=record['FileExtension'], Content=image)
        self.db_photo['Contents'].update(data, ['ItemId'])
        

if __name__ == '__main__':
    hatena_id = 'ytyaru'
    downloader = Downloader(
        hatena_id = hatena_id,
        path_hatena_photolife_sqlite3 = "meta_Hatena.PhotoLife.ytyaru.sqlite3"
    )
    downloader.downloads()

