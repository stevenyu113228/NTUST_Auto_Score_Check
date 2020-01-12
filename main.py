# coding: utf-8
from selenium import webdriver
from PIL import Image
from conf import * #自己ㄉconf檔案
from threading import Timer
import NTUST_verification_code_to_text  #辨識驗證碼用ㄉ
import time
import pandas
import requests
import datetime
import cv2
from selenium.webdriver.common.keys import Keys


def cal_gpa(df):
    print(df)
    sum_of_cred = 0
    sum_of_gpa = 0
    gpa = {
        'A+':4.3,
        'A':4,
        'A-':3.7,
        'B+':3.3,
        'B':3,
        'B-':2.7,
        'C+':2.3,
        'C':2,
        'C-':1.7,
        'D':1,
        'E':0,
        'X':0
    }
    for i in range(1,len(df)+1):
        if (df[:][4][i] != '尚未確認') and (df[:][4][i] != '二次退選'):
            sum_of_gpa += gpa[df[:][4][i]]*int(df[:][3][i])
            sum_of_cred += int(df[:][3][i])
    return "GPA：" + str(sum_of_gpa/sum_of_cred) + "\n"



def dict_to_txt(df):
    rt = cal_gpa(df)
#     dic = df.set_index(2).T.to_dict('records')[1]
    dic = {}

    for i in range(1,len(df[2])+1):
        dic[df[2][i]] = df[4][i]
    
    for d,s in dic.items():
        rt += "{} ： {}".format(d,s) + '\n'
    return rt[:-1]

def chk_is_submit(df):
    dic = df.set_index(2).T.to_dict('records')[1]
    k = 0
    for d,s in dic.items():
        if (s!= '尚未確認') and (s!= '二次退選'):
            k = k+1
    return k

def init_selemium():
    global web
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    web = webdriver.Chrome(options =chrome_options , executable_path = chrome_path)
    web.set_window_size(800,600)


def load_page():
    global web
    try:
        web.get('https://stuinfo8.ntust.edu.tw/ntust_stu/stu.aspx')
    except:
        alert = web.switch_to.alert
        alert.accept()

    try:
        alert = web.switch_to.alert
        alert.accept()
    except:
        pass
    time.sleep(1)
    print("Web Loaded")


def login():
    global web
    studentno = web.find_element_by_name("studentno")
    idcard = web.find_element_by_name("idcard")
    DropMonth = web.find_element_by_name("DropMonth")
    DropDay = web.find_element_by_name("DropDay")
    password = web.find_element_by_name("password")
    code_box = web.find_element_by_name("code_box")
    verify_code = web.find_element_by_id("Image2")
    btn = web.find_element_by_id("Button1")

    web.get_screenshot_as_file("temp.png")
    left = verify_code.location['x']
    right = verify_code.location['x'] + verify_code.size['width']
    top = verify_code.location['y']
    bottom = verify_code.location['y'] + verify_code.size['height']
    im = cv2.imread("temp.png")
    im = cv2.resize(im,(800,600),interpolation=cv2.INTER_CUBIC)
    cv2.imwrite("temp1.png",im)
    img = Image.open("temp1.png")


    img = img.crop((left, top, right, bottom))
    verification_code = NTUST_verification_code_to_text.main(img)

    studentno.send_keys(studentno_)
    idcard.send_keys(idcard_)
    DropMonth.send_keys(DropMonth_)
    DropDay.send_keys(DropDay_)
    password.send_keys(password_)
    code_box.send_keys(verification_code)
    btn.send_keys(Keys.RETURN)
    print("登入成功!",verification_code)



def go_to_search():
    global web
    time.sleep(1)
    web.find_element_by_id("Button2").click()
    print("進入成績查詢")


def read_data():
    global web
    pd = pandas.read_html(web.page_source)
    s_data = pd[4]
    s_data = s_data.drop([0,1,5,6],axis=1)
    s_data = s_data.drop(0)
    web.close()
    print("讀取資料")
    return s_data


def send_request(s_data): #TG
    method = 'sendMessage'
    url = 'https://api.telegram.org/{}/{}'.format(TGtoken,method)
    data = {
        'chat_id':TGid,
        'text':dict_to_txt(s_data),
    }
    res = requests.post(url,data=data)
    print("發送TG request")


def timer_main(inc):
    global n
    if datetime.datetime.now().hour >=8 and datetime.datetime.now().hour <=18:
        init_selemium()
        load_page()
        login()
        go_to_search()
        data = read_data()
        if chk_is_submit(data) > n:
            print("有更新ㄌ!!!")
            n = chk_is_submit(data)
            send_request(data)
        else:
            print("沒有更新QAO")
    else:
        print("現在公務員沒有上班啦= = 不可能更新")

    # 這邊是在callback計時器，我也不懂原理，反正是複製來ㄉ
    t = Timer(inc, timer_main, (inc,))
    t.start()

if __name__ == '__main__':
    global n #要讓他持續活著QAO
    n = -1 #假設現在有-1筆已開獎ㄉ
    timer_main(60*15) #刷新時間(秒)
