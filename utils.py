import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
import json

#웹툰사이트 타입
class Type:
    manamoa = '마나모아'
    naver = '네이버'
    lezhin = '레진'
    daum = '다음'
    wtoon = 'W툰'
    toonkor = '툰코'
    newtoki = '뉴토끼'
    toptoon = '탑툰'
    kakao = '카카오'

#메인페이지 주소
class mainUrl:
    manamoa = ''
    naver = ''
    lezhin = ''
    daum = ''
    wtoon = ''
    toonkor = ''
    newtoki = ''
    toptoon = ''
    kakao = ''

class pageList:
    pageType = ''
    url = ''

#마지막 받은 페이지 저장
def setLastSeq(title, seq):
    try:
        with open('LastSeq.json','rt',encoding='UTF8') as json_file:
            data = json.load(json_file)
        with open('LastSeq.json', 'w', encoding='UTF8') as json_file:
            data[title] = seq
            json.dump(data, json_file, ensure_ascii=False)
    except Exception as ex:
        logger.error(ex)

#마지막 받은 페이지 호출
def getLastSeq(title):
    try:
        with open('LastSeq.json', 'rt', encoding='UTF8') as json_file:
            data = json.load(json_file)
            if title in data :
                seq = data[title]
            else:
                seq = ''

        return seq
    except Exception as ex:
        logger.error(ex)
        return

#json url 로드
def geturl():
    try:
        with open('url.json','rt',encoding='UTF8') as json_file:
            data = json.load(json_file)
            mainUrl.manamoa = data["manamoa"]
            mainUrl.naver = data["naver"]
            mainUrl.daum = data["daum"]
            mainUrl.lezhin = data["lezhin"]
            mainUrl.toptoon = data["toptoon"]
            mainUrl.wtoon = data["wtoon"]
            mainUrl.toonkor = data["toonkor"]
            mainUrl.newtoki = data["newtoki"]

        #URL주소가 유효한지 체크 후 반영
        ChekList()
        with open('url.json','w',encoding='UTF8') as json_file:
            data["wtoon"] = mainUrl.wtoon
            data["manamoa"] = mainUrl.manamoa
            data["newtoki"] = mainUrl.newtoki
            json.dump(data, json_file, ensure_ascii=False)

        logger.info('json로드 완료')
    except Exception as ex:
        logger.error(ex)

#유효한 주소인지 체크
def ChekList():
    url = mainUrl.newtoki
    while True:
        chk = UrlCheck(url, Type.newtoki)
        if chk:
            mainUrl.newtoki = url
            break
        else:
            url = UrlChange(url)

    url = mainUrl.manamoa
    while True:
        chk = UrlCheck(url, Type.manamoa)
        if chk:
            mainUrl.manamoa = url
            break
        else:
            url = UrlChange(url)

    url = mainUrl.wtoon
    while True:
        chk = UrlCheck(url, Type.wtoon)
        if chk:
            mainUrl.wtoon = url
            break
        else:
            url = UrlChange(url)

def UrlCheck(url, type):
    try:
        res = requests.get(url)
        if type == Type.wtoon:
            if not BeautifulSoup(res.text, 'html.parser').find('div', {'class': 'logo'}):
                return False
        logger.info(res)
        return True
    except Exception as ex:
        logger.error(ex)
        return False

def UrlChange(url):
    try:
        old = int(re.findall("\d+",url)[0])
        new = old + 1
        url = str(url).replace(str(old),str(new))
        return url
    except Exception as ex:
        logger.error(ex)

#[] 씌워주기
def bracket(text):
    brackettext = '[' + text + ']'
    return brackettext

#크롤링할 웹툰들 로드
def getList():
    list = []
    try:
        logger.info('리스트 로드')
        with open('list.txt', 'rt', encoding='utf-8') as f:
            div = ''
            lines = f.read().split()
            for line in lines:
                if line.isspace(): continue
                page = pageList()
                if line == bracket(Type.manamoa):
                    div = Type.manamoa
                    continue
                elif line == bracket(Type.daum):
                    div = Type.daum
                    continue
                elif line == bracket(Type.naver):
                    div = Type.naver
                    continue
                elif line == bracket(Type.kakao):
                    div = Type.kakao
                    continue
                elif line == bracket(Type.lezhin):
                    div = Type.lezhin
                    continue
                elif line == bracket(Type.newtoki):
                    div = Type.newtoki
                    continue
                elif line == bracket(Type.toonkor):
                    div = Type.toonkor
                    continue
                elif line == bracket(Type.toptoon):
                    div = Type.toptoon
                    continue
                elif line == bracket(Type.wtoon):
                    div = Type.wtoon
                    continue
                page.pageType = div
                page.url = line
                list.append(page)

        return list
    except Exception as ex:
        logger.error(ex)
