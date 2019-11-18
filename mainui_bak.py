import errno
import os
import re
import sys
import utils
from urllib import parse
import math
import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QAction, qApp, QMainWindow, QDesktopWidget, QPushButton, QVBoxLayout, \
    QLabel, QTextEdit, QListWidget, QCheckBox, QListWidgetItem, QComboBox
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import logging
from selenium.webdriver.common.keys import Keys
logger = logging.getLogger(__name__)
timer = 1



def main():
    list = {}

    list = utils.getList()

    for type, url in list.items():
        login(type, url)

    logger.info('프로그램 종료')
    exit()

class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()  # 초기화

    # TODO 초기화
    def initUI(self):
        self.menu()  # 메뉴
        self.naver = 'https://comic.naver.com'
        self.manamoa = 'https://manamoa14.net'
        self.toonkor = 'https://toonkor.haus'
        self.wtoon = 'https://wtoon17.com'
        self.daum = 'http://webtoon.daum.net'
        self.lezhin = 'https://www.lezhin.com/ko/comic'
        self.top = 'https://toptoon.com'
        self.dic = {}

        self.cb = QComboBox(self)

        self.cb.addItem('탑툰')
        self.cb.addItem('레진')
        self.cb.addItem('뉴토끼')
        self.cb.addItem('다음')
        self.cb.addItem('W툰')
        self.cb.addItem('툰코')
        self.cb.addItem('마나모아')
        self.cb.addItem('네이버')
        self.cb.move(20, 30)
        self.cb.resize(70, 20)

        btn = QPushButton('조회', self)
        btn.setCheckable(True)
        btn.move(400, 30)
        btn.resize(70, 25)
        btn.toggle()
        btn.clicked.connect(self.search)

        self.txt = QTextEdit('https://toptoon.com/weekly/ep_list/the_subjects_contract', self)
        self.txt.setAcceptDrops(False)
        self.txt.move(100, 30)
        self.txt.resize(280, 25)

        self.list = QListWidget(self)
        self.list.move(20, 70)
        self.list.resize(250, 200)

        # self.setLayout()

        self.setWindowTitle('테스트')  # 메인타이틀
        self.setWindowIcon(QIcon('title.png'))  # 메인아이콘
        self.center()  # 위치
        self.resize(500, 300)  # 크기
        self.show()


    # TODO 창위치지정
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    # TODO 메뉴바
    def menu(self):
        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

    #조회
    def search(self):
        url = self.txt.toPlainText()
        type = self.cb.currentText()
        print(url)

        timer = 1
        #selenium 초기화
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument('disable-gpu')

        driver = webdriver.Chrome('chromedriver')  # ,chrome_options=option)

        if(type == '마나모아'):
            #마나모아주소가 맞는지 확인
            regex = re.sub('(https:\/\/)','', re.sub('[0-9]+.(.+?)\/(.+?)*','',url))
            if not(regex == 'manamoa'):
                logger.error('마나모아 주소가 아닙니다 다시 입력해주세요')
                return
            self.list_search(driver, url, type)
        elif(type == '툰코'):
            self.list_search(driver, url, type)
        elif(type == 'W툰'):
            self.list_search(driver, url, type)
        elif (type == '다음'):
            self.paging(driver, url, type)
        elif(type == '네이버'):
            self.paging(driver, url, type)
        elif(type == '레진'):
            self.list_search(driver, url, type)
        elif (type == '뉴토끼'):
            self.list_search(driver, url, type)
        elif(type == '탑툰'):
            self.list_search(driver, url, type)

        driver.quit()
        print('다운끝')

    #페이징처리
    def paging(self, driver, page, type):
        driver.get(page)
        time.sleep(3)
        try:
            # 마지막페이지번호 구하기
            if (type == '다음'):
                self.login(driver, type)
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
                self.list_search(driver, url, type)
        except Exception as ex:
            logger.error(ex)
            logger.error(BeautifulSoup(driver.page_source, 'html.parser').find('span', {'class': 'inner_pages'}))
            self.paging(driver,page,type)

    # 웹툰리스트 조회
    def list_search(self,driver,page,type):
        #option = webdriver.ChromeOptions()
        #option.add_argument('headless')
        #option.add_argument('disable-gpu')

        #driver = webdriver.Chrome('chromedriver')  # ,chrome_options=option)

        driver.get(page)
        time.sleep(timer)
        try:
            if(type == '마나모아'):
                time.sleep(5)
                self.name = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'red title'}).text
                soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'chapter-list'}).find_all('a')
            elif(type == '툰코'):
                self.name = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'title'}).get('content')
                soup = BeautifulSoup(driver.page_source, 'html.parser').find('table', {'class': 'web_list'}).find_all('td',{'class':'content__title'})
            elif(type == 'W툰'):
                self.name = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'title'}).get('content')
                soup = BeautifulSoup(driver.page_source, 'html.parser').find('ul', {'class': 'list'}).find_all('a')
            elif (type == '다음'):
                self.login(driver, type)
                self.name = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'property': 'title'}).get('content')
                if not BeautifulSoup(driver.page_source, 'html.parser').find('ul',{'class': 'clear_g list_update'}).find_all('a', {'class': 'link_wt'}):
                    while True:
                        logger.warning('list loading.....')
                        time.sleep(1)
                        if BeautifulSoup(driver.page_source, 'html.parser').find('ul',{'class': 'clear_g list_update'}).find_all('a', {'class': 'link_wt'}): break
                soup = BeautifulSoup(driver.page_source, 'html.parser').find('ul',{'class': 'clear_g list_update'}).find_all('a', {'class': 'link_wt'})
            elif(type == '네이버'):
                self.name = BeautifulSoup(driver.page_source, 'html.parser').find('title').text.replace(' :: 네이버 만화', '')
                soup = BeautifulSoup(driver.page_source, 'html.parser').find('table', {'class': 'viewList'}).find_all('td',{'class': 'title'})
            elif(type == '레진'):
                self.name = BeautifulSoup(driver.page_source, 'html.parser').find('h2',{'class':'comicInfo__title'}).text
                soup = BeautifulSoup(driver.page_source, 'html.parser').find('ul', {'id': 'comic-episode-list'}).find_all('div',{'class':'episode-name ellipsis'})
            elif (type == '뉴토끼'):
                self.name = BeautifulSoup(driver.page_source, 'html.parser').find('meta', {'name': 'subject'}).get('content')
                soup = BeautifulSoup(driver.page_source, 'html.parser').find('ul', {'class': 'list-body'}).find_all('a',{'class':'item-subject'})
            elif(type == '탑툰'):
                self.name = BeautifulSoup(driver.page_source, 'html.parser').find('span', {'class': 'tit_toon'}).text
                soup = BeautifulSoup(driver.page_source, 'html.parser').find('tbody').find_all('tr',{'class': 'episode_tr'})

            self.name = self.name.replace('/','／').replace('?','？').replace(':','：').replace('|','｜').replace('.','．').strip()
            list = []
            for data in soup:
                if(type == '마나모아'):
                    list.append(self.manamoa + data.get('href'))
                elif(type == '툰코'):
                    list.append(self.toonkor + data.get('data-role'))
                elif (type == 'W툰'):
                    list.append(self.wtoon + data.get('href'))
                elif(type == '다음'):
                    list.append(self.daum + data.get('href'))
                elif(type == '네이버'):
                    list.append(self.naver + data.find('a').get('href'))
                elif(type == '레진'):
                    count = int(data.text)
                    list.append(page + '/' + str(count))
                elif (type == '뉴토끼'):
                    list.append(data.get('href'))
                elif(type == '탑툰'):
                    list.append(page.replace('ep_list','ep_view') + '/' + data.get('data-episode-id'))

            for url in list:
                self.image_search(driver,url,type)

        except Exception as ex:
            logger.error(ex)

        #driver.quit()

    #이미지 조회
    def image_search(self, driver, url, type):
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
                self.login(driver,type)

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
                    id.send_keys("sica4311@naver.com")
                    pw.clear()
                    pw.send_keys("dlawls")
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

        print(self.name,title)
        #print(soup)

        self.download(url,title,soup,type)

    #이미지 다운로드
    def download(self, url, title, img_list, type):
        title = title.replace('/','／').replace('?','？').replace(':','：').replace('|','｜').replace('.','．').strip()
        print(title, '다운시작')

        # 화폴더생성
        #if (type == 'W툰'):
        #    fordername = self.name + '/' + self.name + '_' + title
        #else:
        fordername = self.name + '/' + title
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

    def login(self,driver,type):
        if type == '다음':
            if (BeautifulSoup(driver.page_source, 'html.parser').find('title').text == 'Daum 로그인'):
                login = BeautifulSoup(driver.page_source, 'html.parser').find('a',{'class': 'link_login link_dlogin'}).get('href')
                driver.get(login)
                id = driver.find_element_by_id("id")  # 아이디를 입력할 input 위치
                pw = driver.find_element_by_id("inputPwd")  # 비밀번호를 입력할 input 위치
                login_button = driver.find_element_by_id("loginBtn")  # 로그인버튼
                id.clear()
                id.send_keys("fl2004")
                pw.clear()
                pw.send_keys("dlawls0205")
                login_button.click()
                time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())