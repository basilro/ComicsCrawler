import errno
import os
import re
import utils
from urllib import parse
import math
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import logging
from selenium.webdriver.common.keys import Keys
logger = logging.getLogger(__name__)
timer = 1
urls = utils.mainUrl

toon_name = ''
def main():
    logger.info('프로그램 시작')
    #메인 URL 로드 겸 변경 체크
    utils.geturl()

    #웹툰리스트 로드
    list = utils.getList()
    logger.info(list)

    # selenium 초기화
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('disable-gpu')

    driver = webdriver.Chrome('chromedriver')  # ,chrome_options=option)

    #웹툰페이지 로스 스타트
    for page in list:
        search(driver, page.pageType, page.url)

    driver.quit()

    logger.info('프로그램 종료')
    exit()


#조회
def search(driver, type, url):
    print(url)

    timer = 1

    if(type == '마나모아'):
        list_search(driver, utils.mainUrl.manamoa + url, type)
    elif(type == '툰코'):
        list_search(driver, url, type)
    elif(type == 'W툰'):
        list_search(driver, utils.mainUrl.wtoon + url, type)
    elif (type == '다음'):
        paging(driver, url, type)
    elif(type == '네이버'):
        paging(driver, url, type)
    elif(type == '레진'):
        list_search(driver, url, type)
    elif (type == '뉴토끼'):
        list_search(driver, utils.mainUrl.newtoki + url, type)
    elif(type == '탑툰'):
        list_search(driver, url, type)

#페이징처리
def paging(driver, page, type):
    driver.get(page)
    time.sleep(3) #번호부분이 마지막쯤 로드되서 여유시간을 좀더줌
    try:
        # 마지막페이지번호 구하기
        if (type == '다음'):
            login(driver, type)
            last_no = BeautifulSoup(driver.page_source, 'html.parser').find('span', {'class': 'inner_pages'}).find_all('a',{'class':'link_page'})[-1].text
        elif(type == '네이버'):
            last_no = BeautifulSoup(driver.page_source, 'html.parser').find('td', {'class': 'title'}).find('a').get('href')#['href']
            last_no = math.ceil(int(parse.parse_qs(last_no)['no'][0]) / 10)

        for count in range(1, int(last_no) + 1):
            if(type == '다음'):
                url = page + '#pageNo=' + str(count)
            elif(type == '네이버'):
                url = page + '&page=' + str(count)
            print(url)
            timer = 3
            list_search(driver, url, type)
    except Exception as ex:
        logger.error(ex)
        logger.error(BeautifulSoup(driver.page_source, 'html.parser').find('span', {'class': 'inner_pages'}))
        paging(driver,page,type)

# 웹툰리스트 조회
def list_search(driver,page,type):

    driver.get(page)
    time.sleep(timer)
    try:
        if(type == '마나모아'):
            time.sleep(5)
            toon_name = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'red title'}).text
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'chapter-list'}).find_all('a')
        elif(type == '툰코'):
            toon_name = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'title'}).get('content')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('table', {'class': 'web_list'}).find_all('td',{'class':'content__title'})
        elif(type == 'W툰'):
            toon_name = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'title'}).get('content')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('ul', {'class': 'list'}).find_all('a')
        elif (type == '다음'):
            login(driver, type)
            toon_name = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'property': 'title'}).get('content')
            if not BeautifulSoup(driver.page_source, 'html.parser').find('ul',{'class': 'clear_g list_update'}).find_all('a', {'class': 'link_wt'}):
                while True:
                    logger.warning('list loading.....')
                    time.sleep(1)
                    if BeautifulSoup(driver.page_source, 'html.parser').find('ul',{'class': 'clear_g list_update'}).find_all('a', {'class': 'link_wt'}): break
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('ul',{'class': 'clear_g list_update'}).find_all('a', {'class': 'link_wt'})
        elif(type == '네이버'):
            toon_name = BeautifulSoup(driver.page_source, 'html.parser').find('title').text.replace(' :: 네이버 만화', '')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('table', {'class': 'viewList'}).find_all('td',{'class': 'title'})
        elif(type == '레진'):
            toon_name = BeautifulSoup(driver.page_source, 'html.parser').find('h2',{'class':'comicInfo__title'}).text
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('ul', {'id': 'comic-episode-list'}).find_all('div',{'class':'episode-name ellipsis'})
        elif (type == '뉴토끼'):
            toon_name = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'subject'}).get('content')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('ul', {'class': 'list-body'}).find_all('a',{'class':'item-subject'})
        elif(type == '탑툰'):
            toon_name = BeautifulSoup(driver.page_source, 'html.parser').find('span', {'class': 'tit_toon'}).text
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('tbody').find_all('tr',{'class': 'episode_tr'})

        toon_name = toon_name.replace('/','／').replace('?','？').replace(':','：').replace('|','｜').replace('.','．').strip()
        #마지막 페이지 불러옴
        lastseq = utils.getLastSeq(toon_name)

        list = []
        for data in soup:
            if(type == '마나모아'):
                pageurl = utils.mainUrl.manamoa + data.get('href')
                if lastseq == pageurl : break
                list.append(pageurl)
            elif(type == '툰코'):
                pageurl = utils.mainUrl.toonkor + data.get('data-role')
                if lastseq == pageurl: break
                list.append(pageurl)
            elif (type == 'W툰'):
                pageurl = utils.mainUrl.wtoon + data.get('href')
                if lastseq == pageurl: break
                list.append(pageurl)
            elif(type == '다음'):
                list.append(utils.mainUrl.daum + data.get('href'))
            elif(type == '네이버'):
                list.append(utils.mainUrl.naver + data.find('a').get('href'))
            elif(type == '레진'):
                count = int(data.text)
                list.append(page + '/' + str(count))
            elif (type == '뉴토끼'):
                pageurl = data.get('href')
                if lastseq == pageurl: break
                list.append(pageurl)
            elif(type == '탑툰'):
                pageurl = page.replace('ep_list','ep_view') + '/' + data.get('data-episode-id')
                if lastseq == pageurl: break
                list.append(pageurl)

        #마지막 페이지 저장
        utils.setLastSeq(toon_name, list[0])

        for url in list:
            image_search(driver,url,type)

    except Exception as ex:
        logger.error(ex)

    #driver.quit()

#이미지 조회
def image_search(driver, url, type):
    #print(url)
    driver.get(url)
    time.sleep(timer)
    try:
        if(type == '마나모아'):
            title = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'title'}).get('content')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'view-content scroll-viewer'}).find_all('img')
        elif(type == '툰코'):
            title = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'title'}).get('content')
            # 이미지로딩 체크
            if not BeautifulSoup(driver.page_source, 'html.parser').find('div', {'id': 'toon_img'}).find_all('img'):
                while True:
                    logger.warning('loading.....')
                    time.sleep(1)
                    if BeautifulSoup(driver.page_source, 'html.parser').find('div', {'id': 'toon_img'}).find_all('img') : break
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'id': 'toon_img'}).find_all('img')
        elif (type == 'W툰'):
            title = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'title'}).get('content')
            # 이미지로딩 체크
            if not BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'wbody'}).find_all('img'):
                while True:
                    logger.warning('loading.....')
                    time.sleep(1)
                    if BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'wbody'}).find_all('img'): break
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'wbody'}).find_all('img')
        elif (type == '뉴토끼'):
            loading = '/img/loading-image.gif'
            while True:
                src = BeautifulSoup(driver.page_source, 'html.parser').find('div',{'class': 'view-content'}).find_all('img')[-1].get('src')
                #print(src)
                if(src != loading): break
                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                time.sleep(0.1)

            title = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'subject'}).get('content')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'view-content'}).find_all('img')
        elif(type == '탑툰'):
            if (BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'sns_join2 clearfix'}) != None):
                driver.get(BeautifulSoup(driver.page_source, 'html.parser').find('a',{'class':'action sns_naver2'}).get('href'))

            title = BeautifulSoup(driver.page_source, 'html.parser').find('p', {'class': 'title'}).text + '_' + BeautifulSoup(driver.page_source, 'html.parser').find('p', {'class': 'stitle'}).text.strip()
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'id': 'viewerContentsWrap'}).find_all('img')
        elif (type == '다음'):
            #로그인체크
            login(driver,type)

            #이미지로딩 체크
            if not BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'cont_view'}).find_all('img'):
                while True:
                    logger.warning('loading.....')
                    time.sleep(1)
                    # 유료웹툰 체크
                    chk = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'id': 'payArea'}).find('div', {'class': 'box_payment'})
                    print(chk)
                    if chk != None or not chk : return
                    if BeautifulSoup(driver.page_source, 'html.parser').find('div',{'class': 'cont_view'}).find_all('img'): break
            title = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'property': 'title'}).get('content')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'cont_view'}).find_all('img')

        elif(type == '네이버'):
            title = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'property': 'og:title'}).get('content')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'wt_viewer'}).find_all('img')
        elif(type == '레진'):
            if(BeautifulSoup(driver.page_source, 'html.parser').find('form', {'id': 'login-form'}) != None):
                id = driver.find_element_by_id("login-email")  # 아이디를 입력할 input 위치
                pw = driver.find_element_by_id("login-password")  # 비밀번호를 입력할 input 위치
                chk = driver.find_elements_by_name('remember_me')[1]
                #chk = driver.find_element_by_xpath("//label[@class='lzCheck']")  # 로그인버튼
                #print(id)
                #print(login)
                #login.click()
                #chk.send_keys(Keys.ENTER)
                id.clear()
                id.send_keys("")
                pw.clear()
                pw.send_keys("")
                time.sleep(1)
                chk.send_keys(Keys.ENTER)
                time.sleep(3)
            time.sleep(1)
            title = BeautifulSoup(driver.page_source, 'html.parser').find('title').text.replace(' - 웹툰 - 레진코믹스','')
            soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'id': 'scroll-list'}).find_all('div',{'class':'cut'})
            print(soup)
            #time.sleep(10)
        #return
    except Exception as ex:
        logger.error(ex)

    print(toon_name,title)
    #print(soup)

    download(url,title,soup,type)

#이미지 다운로드
def download(url, title, img_list, type):
    title = title.replace('/','／').replace('?','？').replace(':','：').replace('|','｜').replace('.','．').strip()
    print(title, '다운시작')

    # 화폴더생성
    #if (type == 'W툰'):
    #    fordername = self.name + '/' + self.name + '_' + title
    #else:
    fordername = toon_name + '/' + title
    try:
        if (os.path.isfile(fordername + '.zip')):
            return
        elif not os.path.isdir(fordername):
            os.makedirs(os.path.join(fordername))

    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error('폴더 생성 실패')
            return

    #이미지 다운로드
    filename = 1
    for img in img_list:
        src = img.get('src')
        #print(src)
        try:
            if (type == '마나모아' or type == 'W툰' or type == '다음' or type == '네이버' or type == '레진'):
                res = requests.get(src, headers={'referer': url})
            else:
                res = requests.get(src)
        except Exception as ex:
            logger.error(ex)

        try:
            filefullname = fordername + '/' + str(filename) + '.jpg'
            # print(filefullname)
            if not os.path.isfile(filefullname):
                print(str(filename) + '/' + str(len(img_list)))
                with open(filefullname, 'wb') as f:
                    f.write(res.content)
            filename = filename + 1  # 파일명
        except Exception as ex:
            logger.error(ex)

def login(driver,type):
    if type == '다음':
        if (BeautifulSoup(driver.page_source, 'html.parser').find('title').text == 'Daum 로그인'):
            login = BeautifulSoup(driver.page_source, 'html.parser').find('a',{'class': 'link_login link_dlogin'}).get('href')
            driver.get(login)
            id = driver.find_element_by_id("id")  # 아이디를 입력할 input 위치
            pw = driver.find_element_by_id("inputPwd")  # 비밀번호를 입력할 input 위치
            login_button = driver.find_element_by_id("loginBtn")  # 로그인버튼
            id.clear()
            id.send_keys("")
            pw.clear()
            pw.send_keys("")
            login_button.click()
            time.sleep(1)


main()
