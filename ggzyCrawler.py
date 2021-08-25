import util
import re
import datetime
import os
import smtplib, ssl
import time
import requests
# parse the 广州公共资源交易中心 website
class GGZYCralwer:
    def __init__(self, renderee_root_page) -> None:
        self.root_page = 'http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/index'
        cwd = os.getcwd()
        self.output_dir = os.path.join(cwd, 'output')
        self.today = str(datetime.date.today())

    # https://realpython.com/python-send-email/
    def send_email(self, subject, msg):
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

        with smtplib.SMTP_SSL(self, smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

    def crawl_single_page(self, today, page_cnt):
        #http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/*.jhtml'
        web_link_prefix = r'http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/\d{6}.jhtml'
        label_prefix = r'JG(.*?)]'
        date_prefix = r'<td><span>\d{4}\-\d{2}\-\d{2}</span></td>'

        page_idx = ''
        if page_cnt > 1:
            page_idx = '_'+str(page_cnt)
        cur_page = self.root_page+page_idx+'.jhtml'
        print(f"crawling {cur_page}")
        txt = util.retriable_send_request(cur_page)
        if txt == None:
            return

        web_links = re.findall(web_link_prefix, txt)
        labels = re.findall(label_prefix, txt)
        raw_dates = re.findall(date_prefix, txt)

        #assume the lenth of web_links and labels and raw_dates are the same
        url_info = []
        for i in range(len(web_links)):
            d = re.search(r'\d{4}\-\d{2}\-\d{2}', raw_dates[i]).group()
            if today == None or d == today:
                url_info.append((web_links[i], labels[i], d))

        return url_info

    def get_tenderee(self, file_content):
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

    def crawl_for_the_day(self):
        public_notice_items = []
        if not os.path.exists(self.output_dir):
            print("Working direcotry does not exist")
            return

        page = 1
        while True:
            tmp = self.crawl_single_page(self.today, page)

            if tmp == None or len(tmp) == 0:
                break
            public_notice_items += tmp
            page += 1

        if len(public_notice_items) < 1:
            return
        
        for notice in public_notice_items:
            resp_text = util.retriable_send_request(notice[0])
            tenderee_name = self.get_tenderee(resp_text)
            if tenderee_name == None:
                continue
            tenderee_name = tenderee_name.replace('、', '-')
            print(tenderee_name)

            tenderee_dir = os.path.join(self.output_dir, tenderee_name)
            if not os.path.exists(tenderee_dir):
                os.mkdir(tenderee_dir)

            today_dir = os.path.join(tenderee_dir, self.today)
            if not os.path.exists(today_dir):
                os.mkdir(today_dir)
            file_abs_path = os.path.join(today_dir, f"{notice[1]}.jhtml")
            open(file_abs_path, 'w').write(resp_text)

        # send_email(f"There are {len(public_notice_items)} new public notices", "this is a test message from Jackie")

    def crawl_historical_data(self):
        public_notice_items = []
        if not os.path.exists(self.output_dir):
            print("Working direcotry does not exist")
            return
        page = 1
        while True:
            tmp = self.crawl_single_page(None, page)
            if tmp == None or len(tmp) == 0:
                break
            public_notice_items += tmp
            page += 1

        for notice in public_notice_items:
            resp_text = util.retriable_send_request(notice[0])
            tenderee_name = self.get_tenderee(resp_text)
            if tenderee_name == None:
                continue
            tenderee_name = tenderee_name.replace('、', '-')
            print(tenderee_name)

            tenderee_dir = os.path.join(self.output_dir, tenderee_name)
            if not os.path.exists(tenderee_dir):
                os.mkdir(tenderee_dir)

            today_dir = os.path.join(tenderee_dir, self.today)
            if not os.path.exists(today_dir):
                os.mkdir(today_dir)
            file_abs_path = os.path.join(today_dir, f"{notice[1]}.jhtml")
            open(file_abs_path, 'w').write(resp_text)
