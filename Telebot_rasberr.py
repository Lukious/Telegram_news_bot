# Edit Code lighter for Raspberry pi env

import time
import telepot
import datetime
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from  bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib
# !!!Version ISSUE!!! pip install --upgrade "urllib3==1.22" 
import csv 
import json
from kma import Weather
import pytz
import re
import sys

# Add your telegram bot hash code
bot = telepot.Bot('#')
# Check bot connection
# bot.getMe()
r = open('name.txt', mode='rt', encoding='utf-8')
print(r.read(50000))

r = open('online.txt', mode='rt', encoding='utf-8')
print(r.read(50000))

def get_api_date() :
    standard_time = [2, 5, 8, 11, 14, 17, 20, 23]
    time_now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime('%H')
    check_time = int(time_now) - 1
    day_calibrate = 0
    while not check_time in standard_time :
        check_time -= 1
        if check_time < 2 :
            day_calibrate = 1
            check_time = 23

    date_now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime('%Y%m%d')
    check_date = int(date_now) - day_calibrate
    if check_time < 10:
        check_time = '0'+str(check_time)
    return (str(check_date), (str(check_time) + '00'))

def get_weather_data() :
    # Add your weather service service key
    # check here https://ming9mon.tistory.com/82
    SERVICE_KEY = '#'
    api_date, api_time = get_api_date()
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst?"
    Type = "dataType=json&"
    key = "serviceKey=" + SERVICE_KEY
    date = "&base_date=" + api_date + '&'
    time = "&base_time=" + api_time + '&'
    nx = "&nx=61"
    ny = "&ny=128"
    numOfRows = "numOfRows=100&"
    p_no = "pageNo=1&"
    api_url = url + key + p_no + numOfRows + Type + date + time + nx + ny
    #print(api_url)
    data = urllib.request.urlopen(api_url).read().decode('utf8')
    data_json = json.loads(data)
    
    parsed_json = data_json['response']['body']['items']['item']

    target_date = parsed_json[0]['fcstDate']  # get date and time
    target_time = parsed_json[0]['fcstTime']

    date_calibrate = target_date #date of TMX, TMN
    if target_time > '1300':
        date_calibrate = str(int(target_date) + 1)

    passing_data = {}
    for one_parsed in parsed_json:
        if one_parsed['fcstDate'] == target_date and one_parsed['fcstTime'] == target_time: #get today's data
            passing_data[one_parsed['category']] = one_parsed['fcstValue']

        if one_parsed['fcstDate'] == date_calibrate and (
                one_parsed['category'] == 'TMX' or one_parsed['category'] == 'TMN'): #TMX, TMN at calibrated day
            passing_data[one_parsed['category']] = one_parsed['fcstValue']

    #print(passing_data)
    #print(passing_data['VVV'])
    return passing_data


def Weather():
    weather_info = get_weather_data()
    Weather_Message=''
    
    SKY_list = ['','맑음','구름조금','구름많음','흐림']
    PTY_list = ['눈/비 없음','비','진눈깨비','비']
    
    Weather_Message = Weather_Message + '오늘의 날씨 \n' + '하늘상태 : '+SKY_list[int(weather_info['SKY'])] + '\n강수확률 : ' + weather_info['POP'] + '%\n' + '최고기온 : 섭씨 '+weather_info['TMX']+' 도\n' + '현재기온 : 섭씨 '+weather_info['T3H']+' 도'
    
    if weather_info['PTY'] != '0' or int(weather_info['POP'])>=30:
        Weather_Message = Weather_Message + '\n오늘 눈/비 오니까 꼭 우산 챙기세요!!'
    
    return(Weather_Message)
    
    ''' !!ISSUE MISSING R06 S06!!!
    #!!Rainy test code!! weather_info['R06'] = '1'
    if int(weather_info['R06']) != 0 or int(weather_info['S06']) != 0:
        #!!ISSUE!! Weather_Message = Weather_Message + '강우량 : ' + SKY_list['R06'] +'\n적설량 : ' + SKY_list['S06'] + '\n'
        Weather_Message = Weather_Message + '\n눈/비 오니까 꼭 우산 챙기세요!!'
    '''
    
    
    print(Weather_Message)

def stock_handler(stock):
    kospi = stock

    kos_i = re.sub('<.+?>', '', str(kospi[1]), 0).strip() #현코스피
    kos_b = re.sub('<.+?>', '', str(kospi[4]), 0).strip() #부호 나중에 합침
    kos_p = re.sub('<.+?>', '', str(kospi[2]), 0).strip() # 증감률
    kos_p = kos_b+kos_p # 합쳐서 표시
    kos_per = re.sub('<.+?>', '', str(kospi[3]), 0).strip() # 퍼센트
    kos_b = re.sub('<.+?>', '', str(kospi[4]), 0).strip() # 쓔래기
    kos_com = re.sub('<.+?>', '', str(kospi[6]), 0).strip() # 상승/하락
    
    return kos_i,kos_p,kos_per,kos_com

def issue():
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = 'https://datalab.naver.com/keyword/realtimeList.naver?where=main'
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    data = soup.findAll('span','item_title')
    # title_list = soup.select('att')
    # r1_list = soup.findAll(attrs={'id':'NM_RTK_VIEW_list_wrap'})
    r1_list = soup.findAll(class_="ah_k")
    
    giver = []
    
    for item in data:
        giver.append(str(item.get_text()))
        
    return giver

def issue_News_transector():
    issue_list = issue()
    issue_News_list = []
    for i in range(len(issue_list)):
        #print(str(issue_list[i]))
        issue_News_list.append(News(issue_list[i]))
    # print(issue_News_list[0][0]) #1번뉴스 제목
    # print(issue_News_list[0][0]) #1번뉴스 내용
    return issue_News_list

def random_wiki():
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = 'https://namu.wiki/random'
    o_url = 'https://namu.wiki'
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    data = soup.find('h1')
    # print(data) # 문서이름
    href_link = data.find('a')['href']
    title = re.sub('<.+?>', '', str(data), 0).strip()
    # print(href_link) # 문서 링크(통합해서 전달)
    # print(title)    #문서 이름
    f_link = o_url + href_link
    # print(f_link)  #최종 URL
    wiki_message = ''
    
    wiki_message = wiki_message + '오늘의 랜덤사전 \n' + "문서 제목 : " + title + "\n" + "문서 링크 : " + f_link + '\n'  
    
    return wiki_message
    
def Temp_Corona():
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = 'https://search.naver.com/search.naver?sm=top_sug.pre&fbm=1&acr=1&acq=%EC%BD%94%EB%A1%9C%EB%82%98&qdt=0&ie=utf8&query=%EC%BD%94%EB%A1%9C%EB%82%98+%EB%B0%94%EC%9D%B4%EB%9F%AC%EC%8A%A4+%ED%99%95%EC%A7%84%EC%9E%90'
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    data = soup.find('div',attrs={'class':'state_graph'})
    
    checking = data.find('div',attrs={'class':'circle orange level5'})
    checking = re.sub('<.+?>', '', str(checking), 0).strip()
    
    infected = data.find('div',attrs={'class':'circle red level4'})
    infected = re.sub('<.+?>', '', str(infected), 0).strip()
    
    cured = data.find('div',attrs={'class':'circle blue level2'})
    cured = re.sub('<.+?>', '', str(cured), 0).strip()
    
    dead = data.find('div',attrs={'class':'circle black level2'})
    dead = re.sub('<.+?>', '', str(dead), 0).strip()
    
    corona_mesage = '오늘의 코로나\n' + checking +'\n'+ infected +'\n'+ cured +'\n'+ dead
    
    return corona_mesage


def Dust():
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = 'http://cleanair.seoul.go.kr/air_city.htm?method=measure&grp1=pm10'
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    data = soup.find('tr',attrs={'class':'ft_b ft_point8'})
    mi_dust = data.findAll('td')
    
    
    # dusts = re.sub('<.+?>', '', str(data), 0).strip()
    
    # mi_dust[1] 미세먼지
    # mi_dust[2] 초미세먼지
    # mi_dust[3] 오존
    # mi_dust[4] 이산화질소
    # mi_dust[5] 일산화 탄소
    # mi_dust[5] 아황산가스
    state_list = ['좋음','보통','나쁨','매우나쁨']
    
    m_dust = re.sub('<.+?>', '', str(mi_dust[1]), 0).strip()
    mm_dust = re.sub('<.+?>', '', str(mi_dust[2]), 0).strip()
    oz = re.sub('<.+?>', '', str(mi_dust[3]), 0).strip()
    
    m_state = 0
    mm_state = 0
    
    if int(m_dust) > 0 and  int(m_dust) <= 30:
        m_state = 0
    elif int(m_dust) > 31 and int(m_dust) <= 80 :
        m_state = 1
    elif int(m_dust) > 81 and int(m_dust) <= 150 :
        m_state = 2
    else:
        m_state = 3
        
    if int(mm_dust) > 0 and  int(mm_dust) <= 15:
        mm_state = 0
    elif int(mm_dust) > 16 and int(mm_dust) <= 35 :
        mm_state = 1
    elif int(mm_dust) > 36 and int(mm_dust) <= 75 :
        mm_state = 2
    else:
        mm_state = 3
        
    Dust_msg = "오늘의 미세먼지 \n" + "미세먼지 : " + m_dust + ' '+ state_list[m_state] + "\n초미세먼지 : " + mm_dust+ ' '+ state_list[mm_state] + "\n오존 : " + oz
    
    return Dust_msg

def News(keyward = '인공지능'):
    client_key = "lK_EKLx7kow5ZXKYvy7_" 
    client_secret = "sjgVpv6lIO"
    
    display = 30
    
    encText = urllib.parse.quote(keyward) 
    naver_url = 'https://openapi.naver.com/v1/search/news.json?query=' + encText
    
    request = urllib.request.Request(naver_url)
    request.add_header("X-Naver-Client-Id",client_key)
    request.add_header("X-Naver-Client-Secret",client_secret)
    
    response = urllib.request.urlopen(request)
    
    rescode = response.getcode()

    if(rescode == 200):
        response_body = response.read()
        data = json.loads(response_body)
        news_title_list=[]
        news_des_list=[]
        for i in range(1):   #개수 파라미터
            title = data['items'][i]['title']
            des = data['items'][i]['description']
            # Append해서 처리해야하나...ㅠ
            title = re.sub('<.+?>', '', str(title), 0).strip()
            des = re.sub('<.+?>', '', str(des), 0).strip()
            news_title_list.append(title)
            news_des_list.append(des)
    else:
        print("Error Code:" + rescode)
    
    return news_title_list, news_des_list 

def Issue_handler():
    Issue__Message = '\n실시간 인기검색어 10 \n'
    issue_list = issue()
    for i in range(10):
        Issue__Message = Issue__Message + str((i+1)) +'. '+ issue_list[i] + '\n'
    return Issue__Message    


def Stock():
    # 주식
    url = 'https://finance.naver.com/'
    html=urlopen(url)
    soup=BeautifulSoup(html, "html.parser")
    kospi_tag = soup.findAll('a', attrs={'title':'코스피지수 상세보기'})
    kosdaq_tag = soup.findAll('a', attrs={'title':'코스닥지수 상세보기'})
    kospi = kospi_tag[1].findAll('span')
    kosdaq = kosdaq_tag[1].findAll('span')
    kospi_stock = stock_handler(kospi)
    kosdaq_stock = stock_handler(kosdaq)
    
    Stock_Message = '\n'
    Stock_Message = Stock_Message +'금일 코스피 | '+ kospi_stock[0] + ' \n전일대비 ' + kospi_stock[1] +' '+kospi_stock[2] +' '+ kospi_stock[3]  
    Stock_Message = Stock_Message +'\n\n금일 코스닥 | ' + kosdaq_stock[0] + ' \n전일대비 ' + kosdaq_stock[1] +' '+ kosdaq_stock[2] +' '+ kosdaq_stock[3]
    #print(kospi_stock)
    #print(kosdaq_stock)
    #print(Stock_Message)
    
    return Stock_Message
    
    #print(kosdaq_tag)


def issue_news_handler(issue_news_list):
    issue_list = issue()
    cleared_list = []
    for i in range(10):
        inside = ''
        inside = inside + '<<' +str(issue_list[i]) + '>>'+ '\n' + '제목 : ' + str(issue_news_list[i][0]) + '\n내용 : ' + str(issue_news_list[i][1]) + '\n\n'
        cleared_list.append(inside)
    return cleared_list

def Issue_News_controller(issue_number):
    giver = issue_news_list[issue_number]
    
    return giver


def Daily():
    
    #날씨 (Register KEY ISSUE) 20200227 ->modulization Check 'Weather' Funcion
    '''
    SERVICE_KEY = '#'
    w = Weather(SERVICE_KEY)
    curr = w.get_current()
    forecast = w.get_forecast()
    print('Current temperature: {}'.format(curr.temperature))
    '''
    weather = Weather()
    # print(weather)
    # print(Stock())
    # print(Issue_handler())
    issue_news = issue_News_transector()
    issue_news_list = issue_news_handler(issue_news)
    # print(issue_news_list[1])
    # print(random_wiki())
    # print(Temp_Corona())
    
    Final_Msg = weather +'\n\n' + Dust() + '\n' + Stock() +'\n'+ Issue_handler() +'\n'+ Temp_Corona()+'\n'
    return Final_Msg


def ISSUE_mesger():
    issue_news = issue_News_transector()
    issue_news_list = issue_news_handler(issue_news)
    msg = ''
    for i in range(10):
        msg= msg + issue_news_list[i]
    return msg
        

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    
     
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Press me', callback_data='press')],
                   [InlineKeyboardButton(text='Press me', callback_data='press')],])
    
    
    if content_type == 'text':
        text = msg['text']
        mode = text [:5]
        inputed_data = text[6:]
        print(msg['text'])


        #덱 검색자 시작.
        if '/days' in mode:
            bot.sendMessage(chat_id, Daily())
            
        if  '/isns' in mode:
            bot.sendMessage(chat_id, ISSUE_mesger())
            
        if  'rswws' in mode:
            exit()
            
bot.message_loop(handle)

# Keep the program running.
while 1:
    time.sleep(10)

