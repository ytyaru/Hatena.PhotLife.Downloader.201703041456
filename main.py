#!python3
#encoding:utf-8
import urllib
from urllib.request import build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import CookieJar
import pprint
import dataset
import sys
from bs4 import BeautifulSoup
import datetime
import time
import os.path
import math

class HatenaSite(object):
    def __init__(self, hatena_id, path_hatena_accounts_sqlite3, path_hatena_photolife_sqlite3):
        self.hatena_id = hatena_id
        self.path_hatena_accounts_sqlite3 = path_hatena_accounts_sqlite3
        self.path_hatena_photolife_sqlite3 = path_hatena_photolife_sqlite3
        self.db_accounts = dataset.connect('sqlite:///' + path_hatena_accounts_sqlite3)
        self.db_photo = dataset.connect('sqlite:///' + path_hatena_photolife_sqlite3)
        self.opener = None

    def update(self, subject='Hatena Blog'):
        self.db_photo.begin()
        contents_count = self.db_photo['Contents'].count()
        self.__login()
        if (0 == contents_count):
            self.__all_insert(subject=subject)
        else:
            self.__marge(subject=subject)
        self.db_photo.commit()

    def __login(self):
        account = self.db_accounts['Accounts'].find_one(HatenaId=hatena_id)
        if (None == account):
            print('{0} のはてなIDを持ったアカウント情報は次のDBに存在しません。: {1}'.format(hatena_id, self.path_hatena_accounts_sqlite3))
            sys.exit()
        print(account['Password'])

        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        print(self.opener)
        post = {
            'name': self.hatena_id,
            'password': account['Password']
        }
        data = urlencode(post).encode('utf-8')
        res = self.opener.open('https://www.hatena.ne.jp/login', data)
        pprint.pprint(res.getheaders())
        res.close()

    def __marge(self, subject='Hatena Blog'):
        # DBの最新ItemIdを取得する
        contents_count = self.db_photo['Contents'].count()
        max_item_id = self.db_photo.query('select MAX(ItemId) MaxItemId from Contents;').next()['MaxItemId']
        print("max_item_id={0}".format(max_item_id))
        
        # 1page目でtotalResultsやitemsPerPageを取得する
        rss = self.__request_photolife_rss(subject=subject, page=1, sort='old')
        soup = BeautifulSoup(rss, 'lxml')
        channel = soup.find('channel')
        totalResults = int(channel.find('openSearch:totalResults'.lower()).string)
        startIndex = int(channel.find('openSearch:startIndex'.lower()).string)
        itemsPerPage = int(channel.find('openSearch:itemsPerPage'.lower()).string)
        
        if (contents_count == totalResults):
            print("すでに全件DBに存在します。(totalResultsの値がDBのcount()と一致した)")
            sys.exit()
        
        start_page = math.ceil(contents_count / itemsPerPage)
        all_page_num = math.ceil(totalResults / itemsPerPage)

        # DBの最新ItemIdが存在するページから開始する
        for page in range(start_page, all_page_num + 1):
            rss = self.__request_photolife_rss(subject=subject, page=page, sort='old')
            self.__insert_items_skip(rss, max_item_id)

    def __all_insert(self, subject='Hatena Blog'):       
        # 1page目
        rss = self.__request_photolife_rss(subject=subject, page=1, sort='old')
        self.__insert_items(rss)
        
        # 全ページ数取得
        all_page_num = self.__get_all_page_num(rss)
        
        # 2page目以降(all_page_numが1ならループしない。最後page+1しないと最後pageが含まれない)
        for page in range(1, all_page_num + 1):
            # 1page目を飛ばすために`page+1`する
            rss = self.__request_photolife_rss(subject=subject, page=(page+1), sort='old')
            self.__insert_items(rss)


    """
    はてなフォトライフのRSSを取得する。
    @hatena_id {string}  はてなID。
    @subject   {string}  フォトライフ上のディレクトリ。はてなブログからアップロードした画像はすべて'Hatena Blog'。URLエンコード必須。
    @page      {integer} pageは1以上の整数。
    @sort      {string}  sortは`new`または`old`。
    """
    def __request_photolife_rss(self, subject='Hatena Blog', page=1, sort='new'):
        time.sleep(2)
        url = 'http://f.hatena.ne.jp/{0}/{1}/rss?page={2}&sort={3}'.format(self.hatena_id, subject, page, sort)
        print(url)
        with self.opener.open(url) as res:
            return res.read()
        
    def __get_all_page_num(self, rss):
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#xml
        soup = BeautifulSoup(rss, 'lxml')
        channel = soup.find('channel')
        print(channel)
        totalResults = int(channel.find('openSearch:totalResults'.lower()).string)
        startIndex = int(channel.find('openSearch:startIndex'.lower()).string)
        itemsPerPage = int(channel.find('openSearch:itemsPerPage'.lower()).string)
        print("totalResults={0}".format(totalResults))
        print("startIndex={0}".format(startIndex))
        print("itemsPerPage={0}".format(itemsPerPage))
        # 小数点を切り上げしてPerPage未満のページも1ページ分として加算する
        all_page_num = math.ceil(totalResults / itemsPerPage)
        print("all_page_num={0}".format(all_page_num))
        return all_page_num
        
    def __insert_items(self, rss):
        soup = BeautifulSoup(rss, 'lxml')
        for item in soup.find_all('item'):
            self.__insert_item(item)

    def __insert_item(self, item):
        # .{ext}
        preExt = os.path.splitext(item.find('hatena:imageurl').string)[1]
        # {ext}
        FileExtention = preExt[1:]
        print("FileExtention="+FileExtention)
        
        imageUrl = urllib.parse.urlparse(item.find('hatena:imageurl').string)
        ItemId = os.path.split(imageUrl.path)[1].replace(preExt, "")
        print("imageUrl.path="+imageUrl.path)
        print("ItemId="+ItemId)
        
        self.db_photo['Contents'].insert(dict(
            ItemId=ItemId,
            FileExtention=FileExtention,
            Content=None
        ))
        print(self.db_photo['Contents'].find_one(ItemId=ItemId))

    def __insert_items_skip(self, rss, lastItemId):
        soup = BeautifulSoup(rss, 'lxml')
        for item in soup.find_all('item'):
            preExt = os.path.splitext(item.find('hatena:imageurl').string)[1]
            imageUrl = urllib.parse.urlparse(item.find('hatena:imageurl').string)
            ItemId = os.path.split(imageUrl.path)[1].replace(preExt, "")
            if (lastItemId < ItemId):
                self.db_photo['Contents'].insert(dict(
                    ItemId=ItemId,
                    FileExtention=preExt[1:],
                    Content=None
                ))
                print(self.db_photo['Contents'].find_one(ItemId=ItemId))


if __name__ == '__main__':
    hatena_id = 'ytyaru'
    client = HatenaSite(
        hatena_id = hatena_id,
        path_hatena_accounts_sqlite3 = "meta_Hatena.Accounts.sqlite3",
        path_hatena_photolife_sqlite3 = "meta_Hatena.PhotoLife.ytyaru.sqlite3"
    )
    client.update(subject='Hatena Blog')

