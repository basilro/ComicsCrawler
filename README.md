# ComicsCrawler
웹툰크롤러

site : toonkor, wtoon, naver, daum, manamoa, newtoki, toptoon

20191121 : main.listSearch > setLastSeq 전에 추가
if not (lastseq and type == '다음' and int(re.findall("\d+",lastseq)[0]) > int(re.findall("\d+",list[0])[0])) :
