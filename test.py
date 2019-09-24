import requests
import re

url = 'https://manamoa13.net'
html = ''
check = False
while check != True:
    try:
        print(url)
        html = requests.get(url)
        print(html.ok)
        if html.ok:
            check = True
    except Exception as ex:
        print(ex)
        number = int(re.findall('\d+', url))
        print(number)
        newnumber = number + 1
        url.replace(number,newnumber)
        print('except'+url)


