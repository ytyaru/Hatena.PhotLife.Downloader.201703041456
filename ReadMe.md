# このソフトウェアについて

はてなフォトライフから画像をダウンロードする。

# 開発環境

* Linux Mint 17.3 MATE
* Python 3.4.3
* SQLite 3.8.2

## Webサービス

http://f.hatena.ne.jp/ytyaru/Hatena%20Blog/rss?page=1

# 準備

## DBを作成する

* [はてなアカウントDBを作る](http://ytyaru.hatenablog.com/entry/2017/06/30/000000)
* [はてなブログDBを作る](http://ytyaru.hatenablog.com/entry/2017/07/01/000000)
    * [はてなAPIで取得したXMLからブログ情報を取得しDBに保存する](http://ytyaru.hatenablog.com/entry/2017/07/04/000000)
* [はてなブログ記事DBを作る](http://ytyaru.hatenablog.com/entry/2017/07/02/000000)
    * [はてなAPIで取得したXMLから記事データを取得しDBに保存する](http://ytyaru.hatenablog.com/entry/2017/07/05/000000)
* [はてなフォトライフDBを作る](http://ytyaru.hatenablog.com/entry/2017/07/03/000000)

## 設定する

対象のはてなID、各種DBへのパス、フォトライフのフォルダ名を指定する。

main.py
```python
if __name__ == '__main__':
    hatena_id = 'ytyaru'
    client = HatenaSite(
        hatena_id = hatena_id,
        path_hatena_accounts_sqlite3 = "meta_Hatena.Accounts.sqlite3",
        path_hatena_photolife_sqlite3 = "meta_Hatena.PhotoLife.ytyaru.sqlite3"
    )
    client.update(subject='Hatena Blog')
```

`Hatena Blog`フォルダははてなブログから画像をアップロードしたときに配置される画像を含んだフォルダである。

# 実行

```sh
python3 downloader.py
```

# 結果

フォトライフDBのBLOB型列に画像データが挿入される。

# ライセンス

このソフトウェアはCC0ライセンスである。

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)

なお、使用させていただいたライブラリは以下のライセンスである。感謝。

Library|License|Copyright
-------|-------|---------
[bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)|[MIT](https://opensource.org/licenses/MIT)|[Copyright © 1996-2011 Leonard Richardson](https://pypi.python.org/pypi/beautifulsoup4),[参考](http://tdoc.info/beautifulsoup/)
[dataset](https://dataset.readthedocs.io/en/latest/)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2013, Open Knowledge Foundation, Friedrich Lindenberg, Gregor Aisch](https://github.com/pudo/dataset/blob/master/LICENSE.txt)

