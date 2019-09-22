import errno
import os
import re
import sys
from urllib import response
from urllib.request import urlretrieve
from urllib import parse
import math

import requests
import self as self
import soup as soup
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QAction, qApp, QMainWindow, QDesktopWidget, QPushButton, QVBoxLayout, \
    QLabel, QTextEdit, QListWidget, QCheckBox, QListWidgetItem, QComboBox
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import time


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()  # 초기화

    # TODO 초기화
    def initUI(self):
        self.menu()  # 메뉴
        self.naver = 'https://comic.naver.com'
        self.manamoa = 'https://manamoa14.net'
        self.dic = {}

        self.cb = QComboBox(self)

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

        self.txt = QTextEdit('https://page.kakao.com/viewer?productId=53634510', self)
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


    def search(self):
        url = self.txt.toPlainText()
        type = self.cb.currentText()
        print(url)

        if(type == '마나모아'):
            self.list_search(url)
            return

        if (type == '네이버'):
            html = requests.get(url, headers={'referer': 'https://page.kakao.com/home?seriesId=53634406',
                                              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'})
            print(html)

            return

            # 네이버웹툰 처음페이지조회
            html = requests.get(url, headers={'referer': 'https://comic.naver.com/webtoon/weekday.nhn'})

            # 웹툰명
            self.name = BeautifulSoup(html.text, 'html.parser').find('title').text.replace(' :: 네이버 만화', '')

            # 폴더생성
            try:
                if not (os.path.isdir(self.name)):
                    os.makedirs(os.path.join(self.name))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    print('폴더 생성 실패')
                    exit()

            # 총페이지수 구하기
            page_href = url + '&page='
            last_no = BeautifulSoup(html.text, 'html.parser').find('td', {'class': 'title'}).find('a')['href']
            no = math.ceil(int(parse.parse_qs(last_no)['no'][0]) / 10)
            html.close()
            # print(str(no))

            for page_count in range(1, no + 1):
                # print(page_href+str(page_count))
                page = page_href + str(page_count)
                # print(page)
                self.naver_list_search(page)

        '''썸네일 다운
        day_list = soup.find('div', {'class': 'col_inner'})
        li_list = []
        #for data in day_list:
        #    li_list.extend(data.findAll('li'))
        li_list.extend(day_list.findAll('li'))
        for li in li_list:
            img = li.find('img')
            title = img['title']
            img_src = img['src']
            print(title, img_src)
            urlretrieve(img_src, './webtoon/' + title + '.jpg')
        '''

        '''요일별 타이틀 구하기
        day_list = soup.findAll('div',{'class':'col_inner'})
        for day in day_list:
            data = day.findAll('a',{'class':'title'})
            title_list = [t.text for t in data]
            pprint(title_list)
        '''

    def list_search(self,page):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument('disable-gpu')

        driver = webdriver.Chrome('chromedriver')  # ,chrome_options=option)

        driver.get('https://manamoa14.net/bbs/page.php?hid=manga_detail&manga_id=10857')
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': 'chapter-list'}).find_all('a')
        for data in soup:
            print(data.get('href'))

        driver.quit()

    # 네이버웹툰 리스트목록별 조회
    def naver_list_search(self, page):
        print('list_search', page)
        html = requests.get(page, headers={'referer': 'https://comic.naver.com/webtoon/weekday.nhn'})
        soup = BeautifulSoup(html.text, 'html.parser').find('table', {'class': 'viewList'}).findAll('td',{'class': 'title'})
        html.close()

        a_list = []
        for data in soup:
            a_list.append(data.find('a'))

        # 리스트 사전에 담기
        for a in a_list:
            # print(a)
            title = re.sub('<.+?>', '', str(a), 0).strip()  # 태그제거
            # print(title)
            link = a['href']
            # print(link)
            self.dic[title] = self.naver + link

        # 리스트별조회
        for title in self.dic:
            print(self.dic[title])
            self.image_download(title, self.dic[title])


    # 네이버웹툰 이미지 다운로드
    def image_download(self, title, url):
        print('image_download', title, url)
        # 화폴더생성
        try:
            if not (os.path.isdir(self.name + '/' + title)):
                os.makedirs(os.path.join(self.name + '/' + title))
            else:
                return  # 폴더가 있으면 다운받은 목록이라고 생각하고 다운안함
        except OSError as e:
            if e.errno != errno.EEXIST:
                print('폴더 생성 실패')
                exit()

        html = requests.get(url, headers={'referer': 'https://comic.naver.com/webtoon'})
        # print(html, html.text)
        soup = BeautifulSoup(html.text, 'html.parser')
        # print(soup)
        html.close()

        viewer = soup.findAll('div', {'class': 'wt_viewer'})
        img_list = []
        # print(img_list)
        for tag in viewer:
            # print(tag)
            img_list.extend(tag.findAll('img'))
            # print(id, src)

        src_list = []
        for img in img_list:
            # print(img['src'])
            src_list.append(img['src'])

        # print(src_list)
        filename = 1  # 파일명은 1~ 순서대로
        # 이미지 다운요청 그냥하면 referer없어서 다운이안되는관계로 빈값생성후 바이너리데이터를 넣어준다
        try:
            for url in src_list:
                res = requests.get(url, headers={'referer': self.txt.toPlainText()})
                # print('성공',res)
                image_data = res.content
                # print('이미지정보',image_data)
                filefullname = self.name + '/' + title + '/' + str(filename) + '.jpg'  # 경로+파일명
                filename = filename + 1  # 파일명
                print('파일명', filefullname)
                with open(filefullname, 'wb') as f:
                    f.write(image_data)
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())