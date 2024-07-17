# coding=utf-8
# !/usr/bin/python
import sys
import json
import time
from os.path import splitext

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):  # 元类 默认的元类 type
    alisttoken = ''
    def getName(self):
        return "Alist"

    def init(self, extend):
        try:
            self.ext = extend
        except:
            self.ext = ''

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        result = {}
        if self.ext.startswith('http'):
            url = self.ext
            drivers = self.fetch(url, headers=self.header, timeout=5).json()['drives']
        else:
            drivers = json.loads(self.ext)['drives']
        classes = []
        for driver in drivers:
            if 'hidden' in driver and driver['hidden']:
                continue
            tid = driver['server']
            if 'login' in driver:
                tid = tid + '&&&login' + json.dumps(driver['login'], ensure_ascii=False)
            if 'params' in driver:
                tid = tid + '&&&params' + json.dumps(driver['params'], ensure_ascii=False)
            classes.append({
                'type_name': driver['name'],
                'type_id': tid
            })
        result['class'] = classes
        return result

    def homeVideoContent(self):
        result = {}
        return result

    def categoryContent(self, cid, page, filter, ext):
        result = {}
        login = {}
        params = []
        password = ''
        if '&&&' in cid:
            cidList = cid.split('&&&')
            url = cidList[0]
            for cL in cidList:
                if cL.startswith('login'):
                    login = json.loads(cL.replace('login', ''))
                elif cL.startswith('params'):
                    params = json.loads(cL.replace('params', ''))
        else:
            url = cid
        if url.count('/') == 2:
            url = url + '/'
        header = self.header.copy()
        baseUrl = self.getCache('baseUrl')
        if not baseUrl:
            baseUrl = self.regStr(reg="(http.*://.*?/)", src=url)
        header['Referer'] = baseUrl
        token = self.getCache('alistToken')
        if token:
            token = token['token']
        else:
            data = self.postJson(baseUrl + 'api/auth/login', json=login, headers=header).json()
            if data['code'] == 200:
                token = data['data']['token']
                self.setCache('alistToken', {'token': token, 'expiresAt': int(time.time()) + 86400})
        header['Authorization'] = token
        path = '/' + url.replace(baseUrl, "")
        if path != '/':
            aid = path.strip('/') + '/'
        else:
            aid = path
        for param in params:
            if param['path'].startswith(path) and 'pass' in param:
                password = param['pass']
                break
        param = {
            "path": path,
            'password': password
        }
        r = self.postJson(baseUrl + 'api/fs/list', json=param, headers=header)
        vodList = json.loads(self.cleanText(r.text))['data']['content']
        videos = []
        subtList = []
        playList = []
        for vod in vodList:
            if len(vod['thumb']) == 0:
                img = "./qyg11.png"
            elif vod['thumb'].startswith('http'):
                img = vod['thumb']
            else:
                img = baseUrl.strip('/') + vod['thumb']
            if vod['type'] == 1:
                tag = "folder"
                remark = "文件夹"
                cid = baseUrl + aid + vod['name']
            else:
                if splitext(vod['name'])[1] in ['.mp4', '.mpg', '.mkv', '.ts', '.TS', '.avi', '.flv', '.rmvb', '.mp3', '.flac', '.wav', '.wma', '.dff']:
                    size = self.getSize(vod['size'])
                    tag = "file"
                    remark = size
                    cid = baseUrl + aid + vod['name']
                    playList.append(vod['name'])
                elif splitext(vod['name'])[1] in ['.ass', '.ssa', '.srt']:
                    subtList.append(vod['name'])
                    continue
                else:
                    continue
            if login != {}:
                cid = cid + '&&&login' + json.dumps(login, ensure_ascii=False)
            elif params != []:
                cid = cid + '&&&params' + json.dumps(params, ensure_ascii=False)
            videos.append({
                "vod_id": cid,
                "vod_name": vod['name'],
                "vod_pic": img,
                "vod_tag": tag,
                "vod_remarks": remark
            })
        if playList != []:
            cid = baseUrl + aid
            for pL in playList:
                cid = cid + '!!!' + pL
            if login != {}:
                cid = cid + '&&&login' + json.dumps(login, ensure_ascii=False)
            elif params != []:
                cid = cid + '&&&params' + json.dumps(params, ensure_ascii=False)
            videos.insert(0, {
                "vod_id": cid,
                "vod_name": '播放列表',
                "vod_pic": "https://avatars.githubusercontent.com/u/97389433?s=200&v=4",
                "vod_tag": 'file',
                "vod_remarks": path
            })
        if subtList != []:
            self.setCache(f"subtList_{baseUrl+aid.strip('/')}", {'subtList': subtList, 'expiresAt': int(time.time()) + 86400})
        result['list'] = videos
        result['page'] = 1
        result['pagecount'] = 1
        result['limit'] = len(videos)
        result['total'] = len(videos)
        return result

    def detailContent(self, did):
        did = did[0]
        if '&&&' in did:
            pos = did.index('&&&')
            url = did[:pos]
            append = did[pos:]
        else:
            url = did
            append = ''
        name = url[url.strip('/').rfind('/') + 1:].strip('/')
        if '!!!' in url:
            urls = url.split('!!!')
            fileList = urls[1:]
            url = urls[0]
            playUrl = ''
            for file in fileList:
                playUrl += file + '$' + url + file + append + '#'
        else:
            playUrl = name + '$' + did
            name = did[did.rfind('/') + 1:]
            if '&&&' in name:
                name = name.split('&&&')[0]
        vod = {
            "vod_id": did,
            "vod_name": name,
            "vod_play_from": "Alist网盘",
            "vod_play_url": playUrl.strip('#')
        }
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        return self.searchContentPage(key, quick, '1')

    def searchContentPage(self, key, quick, page):
        result = {'list': []}
        return result

    def playerContent(self, flag, pid, vipFlags):
        result = {}
        purl = self.getDownloadUrl(pid)
        url = pid[:pid.rfind('/')]
        data = self.getCache(f'subtList_{url}')
        subs = []
        if data:
            subList = data['subtList']
            for sub in subList:
                subformat = splitext(sub)[1]
                if subformat == '.srt':
                    sformat = 'application/x-subrip'
                elif subformat == '.ass':
                    sformat = 'application/x-subtitle-ass'
                elif subformat == '.ssa':
                    sformat = 'text/x-ssa'
                else:
                    sformat = 'text/plain'
                surl = url + '/' + sub
                subs.append({'url': f'http://127.0.0.1:UndCover/proxy?do=py&type=sub&url={surl}&sformat={sformat}', 'name': sub, 'format': sformat})
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = purl
        result["header"] = ''
        result["subs"] = subs
        return result

    def getSize(self, size):
        if size > 1024 * 1024 * 1024 * 1024.0:
            fs = "TB"
            sz = round(size / (1024 * 1024 * 1024 * 1024.0), 2)
        elif size > 1024 * 1024 * 1024.0:
            fs = "GB"
            sz = round(size / (1024 * 1024 * 1024.0), 2)
        elif size > 1024 * 1024.0:
            fs = "MB"
            sz = round(size / (1024 * 1024.0), 2)
        elif size > 1024.0:
            fs = "KB"
            sz = round(size / (1024.0), 2)
        else:
            fs = "KB"
            sz = round(size / (1024.0), 2)
        return str(sz) + fs

    def localProxy(self, params):
        url = self.getDownloadUrl(params['url'])
        baseUrl = self.getCache('baseUrl')
        if not baseUrl:
            baseUrl = self.regStr(reg="(http.*://.*?/)", src=params['url'])
        header = self.header.copy()
        header['Referer'] = baseUrl
        content = self.fetch(url, headers=header).content.decode()
        contentTyep = params['sformat']
        action = {'url': '', 'header': header, 'param': '', 'type': 'string'}
        return [200, contentTyep, action, content]

    def getDownloadUrl(self, url):
        params = []
        password = ''
        login = {}
        if '&&&' in url:
            urlList = url.split('&&&')
            url = urlList[0]
            for uL in urlList:
                if uL.startswith('login'):
                    login = json.loads(uL.replace('login', ''))
                elif uL.startswith('params'):
                    params = json.loads(uL.replace('params', ''))
        if url.count('/') == 2:
            url = url + '/'
        header = self.header.copy()
        baseUrl = self.getCache('baseUrl')
        if not baseUrl:
            baseUrl = self.regStr(reg="(http.*://.*?/)", src=url)
        header['Referer'] = baseUrl
        token = self.getCache('alistToken')
        if token:
            token = token['token']
        else:
            data = self.postJson(baseUrl + 'api/auth/login', json=login, headers=header).json()
            if data['code'] == 200:
                token = data['data']['token']
                self.setCache('alistToken', {'token': token, 'expiresAt': int(time.time()) + 86400})
        header['Authorization'] = token
        path = '/' + url.replace(baseUrl, "")
        for param in params:
            if param['path'].startswith(path) and 'pass' in param:
                password = param['pass']
                break
        param = {
            "path": path,
            'password': password
        }
        r = self.postJson(baseUrl + 'api/fs/get', json=param, headers=header)
        url = json.loads(self.cleanText(r.text))['data']['raw_url']
        if not url.startswith('http'):
            url = baseUrl + url.strip('/')
        return url

    def getCache(self, key):
        value = self.fetch(f'http://127.0.0.1:9978/cache?do=get&key={key}', timeout=5).text
        if len(value) > 0:
            if value.startswith('{') and value.endswith('}') or value.startswith('[') and value.endswith(']'):
                value = json.loads(value)
                if type(value) == dict:
                    if not 'expiresAt' in value or value['expiresAt'] >= int(time.time()):
                        return value
                    else:
                        self.delCache(key)
                        return None
            return value
        else:
            return None

    def setCache(self, key, value):
        if len(value) > 0:
            if type(value) == dict or type(value) == list:
                value = json.dumps(value, ensure_ascii=False)
        self.post(f'http://127.0.0.1:9978/cache?do=set&key={key}', data={"value": value}, timeout=5)

    def delCache(self, key):
        self.fetch(f'http://127.0.0.1:9978/cache?do=del&key={key}', timeout=5)

    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"}

if __name__ == "__main__":
    # res = Spider().categoryContent('http://lmhome.leuse.top:8889/LmHome/sdb1/Medias/电视剧/半泽直树(2013)&&&login{"username": "le", "password": "LeMing041390"}', 1, False, {})
    # res = Spider().detailContent(['http://lmhome.leuse.top:8889/LmHome/sdb1/Medias/电视剧/半泽直树(2013)/半泽直树S01E01.mkv&&&login{"username": "le", "password": "LeMing041390"}'])
    res = Spider().playerContent('', 'http://lmhome.leuse.top:8889/LmHome/sdb1/Medias/电视剧/半泽直树(2013)/半泽直树S01E01.mkv&&&login{"username": "le", "password": "LeMing041390"}', '')
    print(res)