import util
import re
import datetime
import os
import smtplib, ssl
import uuid

# parse the 广州公共资源交易中心 website
class GGZYCralwer:
    def __init__(self, renderee_root_page) -> None:
        self.root_page = 'http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/index'
        cwd = os.getcwd()
        self.output_dir = os.path.join(cwd, 'output')
        self.today = str(datetime.date.today())
        self.min_year = 2011

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
            return None

        web_links = re.findall(web_link_prefix, txt)
        labels = re.findall(label_prefix, txt)
        raw_dates = re.findall(date_prefix, txt)
        if len(labels) < len(web_links):
            labels = []
            for i in range(len(web_links)):
                labels.append(str(uuid.uuid4()))

        #assume the lenth of web_links and labels and raw_dates are the same
        url_info = []
        for i in range(len(web_links)):
            d = re.search(r'\d{4}\-\d{2}\-\d{2}', raw_dates[i]).group()
            if int(d[:4]) < self.min_year:
                return None
            if today == None or d == today:
                url_info.append((web_links[i], labels[i], d))

        return url_info

    def get_tenderee(self, file_content):
        tenderee_regexs = [ 
                            r"标 单 位：</span><(.*?)></span",
                            r"标 单 位：</span><(.*?)</span",
                            r"标 单 位(.*?)></span",
                            r"标 单 位(.*?)</span", 
                            r"标 单 位：(.*?)><span",
                            r"标 单 位：(.*?)<span",

                            r"标单 位：</span><(.*?)></span",
                            r"标单 位：</span><(.*?)</span",
                            r"标单 位(.*?)></span",
                            r"标单 位(.*?)</span", 
                            r"标单 位：(.*?)><span",
                            r"标单 位：(.*?)<span",

                            r"招标单位：(.*?)<spanlang",
                            r"招标单位：(.*?)<span ",
                            r"招标单位：(.*?)<span", 
                            r"招标单位：<(.*?)</SPAN", 
                            r"招标单位：(.*?)><SPAN", 
                            r"招标单位：(.*?)<SPAN", 
                            r"招标单位：(.*?)></span",
                            r"招标单位：(.*?)</span>",
                            r"招标单位：(.*?)></SPAN",
                            r"招标单位：(.*?)</SPAN",

                            r"招标人：<(.*?)></span",
                            r"招标人：<(.*?)</span",
                            r"招标人：<(.*?)></SPAN", 
                            r"招标人：<(.*?)</SPAN", 
                            r"招标人：<(.*?)><span",
                            r"招标人：<(.*?)<span",
                            r"招标人：<(.*?)><SPAN", 
                            r"招标人：<(.*?)<SPAN",   

                            r"招标人：(.*?)></span",
                            r"招标人：(.*?)</span",
                            r"招标人：(.*?)></SPAN", 
                            r"招标人：(.*?)</SPAN", 
                            r"招标人：(.*?)><span",
                            r"招标人：(.*?)<span",
                            r"招标人：(.*?)><SPAN", 
                            r"招标人：(.*?)<SPAN"]
        txt = []
        potential_names = []
        # get all potential names, and find the one that's shortest in length. We assume that's
        # closest to truth
        for tr in tenderee_regexs:
            txt = re.findall(tr, file_content)
            if len(txt) == 1 and len(txt[0]) > 1:
                txt[0] = txt[0].replace('宋体', '')
                if re.match('^[0-9a-zA-Z_/><!:; &=\.\?\-\'\"%]*$', txt[0]) == None:
                    potential_names.append(txt[0])
        if len(potential_names) == 0:
            return None

        min_name = ""
        for pn in potential_names:
            if min_name == "" or len(pn) < len(min_name):
                min_name = pn
        # remove all tags behind known keywords
        rm_keys = ["中心","公司","厅","政府","海关","会","队","社","局","学","院","室", "店"]
        for rk in rm_keys:
            pos = min_name.find(rk)
            if pos > 1:
                min_name = min_name[:pos+len(rk)]
                break
        # further remove any tags
        remove_tags = ['<span lang=EN-US>','<spanlang=EN-US>','</u>','<u>','</span>',
        '</span','<span>','<span','<o:p>','</o:p>','</o:p', '<p>', '<p','</p>', 
        '</p', '</li>','</li','<li>','<li','<a>','</a>','<a','</a', '&nbsp;']
        for rt in remove_tags:
            min_name = min_name.replace(rt, '')

        # idx = min_name.rfind('>')
        # tenderee_name = min_name[idx+1:]
        idx = min_name.rfind('>')
        tenderee_name = min_name[idx+1:]
        idx = tenderee_name.rfind('：')
        tenderee_name = tenderee_name[idx+1:]
        idx = tenderee_name.rfind(':')
        tenderee_name = tenderee_name[idx+1:]
        idx = tenderee_name.find('<')
        if idx >=0:
            tenderee_name = tenderee_name[:idx]
        idx = tenderee_name.find('&')
        if idx >= 0:
            tenderee_name = tenderee_name[:idx]
        idx = tenderee_name.find('；')
        if idx >= 0:
            tenderee_name = tenderee_name[:idx]
        idx = tenderee_name.find('; ')
        if idx >= 0:
            tenderee_name = tenderee_name[:idx]    
        idx = tenderee_name.find('。')
        if idx >= 0:
            tenderee_name = tenderee_name[:idx]
        tenderee_name = tenderee_name.strip()
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
            if resp_text == None:
                continue
            tenderee_name = self.get_tenderee(resp_text)
            if tenderee_name == None or tenderee_name == "":
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
            if resp_text == None:
                continue
            tenderee_name = self.get_tenderee(resp_text)
            if tenderee_name == None:
                continue
            tenderee_name = tenderee_name.replace('、', '-')
            print(tenderee_name)

            tenderee_dir = os.path.join(self.output_dir, tenderee_name)
            if not os.path.exists(tenderee_dir):
                os.mkdir(tenderee_dir)

            date_dir = os.path.join(tenderee_dir, notice[2])
            if not os.path.exists(date_dir):
                os.mkdir(date_dir)
            file_abs_path = os.path.join(date_dir, f"{notice[1]}.jhtml")
            open(file_abs_path, 'w').write(resp_text)

    def compute_summary(self):
        if not os.path.exists(self.output_dir):
            print(f"{self.output_dir} doesn't exist")
            return False
        
        renderee_summary = {}
        for renderee_name in os.listdir(self.output_dir):
            
            renderee_dir = os.path.join(self.output_dir, renderee_name)
            if renderee_name == '.' or renderee_name == '..' or os.path.isdir(renderee_dir) == False or renderee_name.startswith('20'):
                continue
            if renderee_name not in renderee_summary:
                renderee_summary[renderee_name] = {}
                year_start = datetime.date.today().year
                for yr in range(year_start, self.min_year-1, -1):
                    renderee_summary[renderee_name][yr] = 0
                

            year_lookup = renderee_summary[renderee_name]
            for dated_dir in os.listdir(renderee_dir):
                if dated_dir == '.' or dated_dir == '..':
                    continue
                year = int(dated_dir[:4])
                count = len(os.listdir(os.path.join(renderee_dir, dated_dir)))
                if year in year_lookup:
                    year_lookup[year] += count
                else:
                    year_lookup[year] = count
        today_dir = os.path.join(self.output_dir, "summary_"+str(datetime.date.today())+".csv")
        this_year = datetime.date.today().year
        title ="招标人，"
        for y in range(this_year, self.min_year-1, -1):
            title+=f"{y},"
        title+="\n"


        with open(today_dir, 'w') as out_file:
            out_file.write(title)
            txt = ""
            for k, v in renderee_summary.items():
                txt += k+","
                for y in range(this_year, self.min_year-1, -1):
                    txt+=f"{v[y]},"
                txt +='\n'
            out_file.write(txt)
