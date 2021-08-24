import requests
import re
import datetime
import os
import smtplib, ssl
import time

public_notice_root_page = 'http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/index.jhtml'

# https://realpython.com/python-send-email/
def send_email(subject, msg):
    port = 465  # For SSL
    password = os.environ['blah']

    smtp_server = "smtp.gmail.com"
    sender_email = "mrjackies@gmail.com"  # Enter your address
    receiver_email = "jannine119@gmail.com"  # Enter receiver address
    # receiver_email = "mrjackies@hotmail.com"  # Enter receiver address

    message = f"""\
    Subject: {subject}

    This message is sent from Jackie."""


    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def crawl_single_page(root_page, output_dir, today, page_cnt):
    web_link_prefix = r'http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/\d{6}.jhtml'#http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/*.jhtml'
    label_prefix = r'JG(.*?)]'
    date_prefix = r'<td><span>\d{4}\-\d{2}\-\d{2}</span></td>'

    page_idx = ''
    if page_cnt > 1:
        page_idx = '_'+str(page_cnt)
    root_page = 'http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/index'+page_idx+'.jhtml'
    r = requests.get(root_page, allow_redirects=True)
    txt = r.text

    web_links = re.findall(web_link_prefix, txt)
    labels = re.findall(label_prefix, txt)
    raw_dates = re.findall(date_prefix, txt)

    #assume the lenth of web_links and labels and raw_dates are the same
    url_info = []
    for i in range(len(web_links)):
        d = re.search(r'\d{4}\-\d{2}\-\d{2}', raw_dates[i]).group()
        if d == today:
            url_info.append((web_links[i], labels[i], d))
    r.close()
    return url_info

def get_tenderee(file_content):
    tenderee = ""
    tenderee_regexs = [r"标 单 位(.*?)</span></span>", r"招标单位：(.*?)&emsp;&emsp;</span>",r"招标人：(.*?)</span></li>"]
    txt = []
    for tr in tenderee_regexs:
        txt = re.findall(tr, file_content)
        if len(txt) == 1:
            break
    if len(txt) == 0:
        return None
    idx = txt[0].rfind('>')
    tenderee_name = txt[0][idx+1:]
    return tenderee_name


cwd = os.getcwd()
output_dir = os.path.join(cwd, 'output')
public_notice_items = []
if not os.path.exists(output_dir):
    print("Working direcotry does not exist")
    exit()

today = str(datetime.date.today())
page = 1
while True:
    tmp = crawl_single_page(public_notice_root_page, output_dir, today, page)
    time.sleep(1)
    if len(tmp) == 0:
        break
    public_notice_items += tmp
    page += 1

if len(public_notice_items) > 0:
    for notice in public_notice_items:
        success = False
        retry_cnt = 0
        # if we got connection error, we will retry 3 times. 
        while not success and retry_cnt < 3:
            try:
                success = True
                req = requests.get(notice[0], allow_redirects=True)
                tenderee_name = get_tenderee(req.text)
                if tenderee_name == None:
                    continue
                tenderee_name = tenderee_name.replace('、', '-')
                print(tenderee_name)

                tenderee_dir = os.path.join(output_dir, tenderee_name)
                if not os.path.exists(tenderee_dir):
                    os.mkdir(tenderee_dir)

                today_dir = os.path.join(tenderee_dir, today)
                if not os.path.exists(today_dir):
                    os.mkdir(today_dir)
                file_abs_path = os.path.join(today_dir, f"{notice[1]}.jhtml")
                open(file_abs_path, 'wb').write(req.content)

                req.close()
            except requests.exceptions.ConnectionError as e:
                print(f"Got connection error {e} for {notice[0]} on {notice[2]}, will retry")
                time.sleep(1)
                retry_cnt += 1
                success = False


        
    # send_email(f"There are {len(public_notice_items)} new public notices", "this is a test message from Jackie")

