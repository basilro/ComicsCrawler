import os
import sys
from datetime import datetime
import logging
import requests
import re

manamoa = 'https://manamoa13.net'
a = '마나모아'
b = '툰코'
c = '네이버'
d = 'W툰'
list = {}
logger = logging.getLogger(__name__)

def main():
    init()
    #url_check(manamoa)
    list_load()
    pass

#url 변경유무 체크
def url_check(url):
    fun = '[url_check] '
    a=1
    while True:
        try:
            logger.info(url)
            if a==10:
                break
            html = requests.get(url)
            if html.ok:
                break

        except Exception as ex:
            logger.error('Exception:',ex)
            a += 1
            number = int(re.findall('\d+', url)[0])
            logger.warning(fun+number)
            newnumber = number + 1
            url = url.replace(str(number),str(newnumber))
            logger.warning(fun+'except'+url)
    pass

#예약리스트
def list_load():
    fun = '[list_load] '
    if not os.path.isfile('list.txt'):
        logger.error(fun+'리스트파일이 존재하지 않습니다')
        sys.exit()

    with open('list.txt', 'r', encoding='utf-8') as f:
        div = ''
        lines = f.read().split()
        for line in lines:
            if line.isspace(): continue
            if line == '[마나모아]':
                div = a
                continue
            elif line == '[툰코]':
                div = b
                continue
            elif line == '[네이버]':
                div = c
                continue
            elif line == '[W툰]':
                div = d
                continue
            list[div] = line

        logger.info(fun+str(list))

#초기화
def init():
    #로그초기화
    today = datetime.today().strftime('%Y%m%d')
    filename = 'log_' + today + '.txt'
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(filename,'a',encoding = "UTF-8")
    streamHandler = logging.StreamHandler()
    logger.addHandler(file_handler)
    logger.addHandler(streamHandler)

def log(fun,txt):


#기타정보남기기
def txt_write(txt):
    filename = 'etc.txt'
    if os.path.isfile(filename):
        with open(filename, 'a', encoding='utf-8') as f:
            f.write('\n')
            f.write(txt)
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(txt)

main()