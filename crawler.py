import requests
import re
import datetime
import os
import smtplib, ssl

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


def crawl_single_page(root_page, working_dir, today, page_cnt):
    web_link_prefix = r'http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/\d{6}.jhtml'#http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/*.jhtml'
    label_prefix = r'JG\d{4}\-\d{5}'
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
    
    return url_info



cwd = os.getcwd()
working_dir = os.path.join(cwd, '')
public_notice_items = []
if not os.path.exists(working_dir):
    print("Working direcotry does not exist")
    exit()

today = str(datetime.date.today())
page = 1
while True:
    tmp = crawl_single_page(public_notice_root_page, working_dir, today, page)
    if len(tmp) == 0:
        break
    public_notice_items += tmp
    page += 1
if len(public_notice_items) < 0:
    exit()

today_dir = os.path.join(working_dir, today)
if len(public_notice_items) > 0:
    if not os.path.exists(today_dir):
        os.mkdir(today_dir)
    for notice in public_notice_items:
        req = requests.get(notice[0], allow_redirects=True)
        file_abs_path = os.path.join(today_dir, f"{notice[1]}.jhtml")
        open(file_abs_path, 'wb').write(req.content)
    send_email(f"There are {len(public_notice_items)} new public notices", "this is a test message from Jackie")

