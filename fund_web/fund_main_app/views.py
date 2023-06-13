# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
import pymysql
import json
import re
import requests
from django.views import View
import time
import fund_main_app.web_socket
import datetime
from django.http import JsonResponse
import hashlib
from chinese_calendar import is_workday
import datetime
from bs4 import BeautifulSoup

from fund_web.settings import DB_PASSWORD, DB_IPADDRESS


# Create your views here.
def _fund_floating():
    fund_list = ["004746", "013291", "008888", "013048", "002351"]
    ret = {}
    for fund in fund_list:
        tt_cookie = "qgqp_b_id=7110e64f9def8a6d6521b2453aff65fa; em_hq_fls=js; HAList=a-sh-600760-%u4E2D%u822A%u6C88%u98DE%2Ca-sz-002024-%u82CF%u5B81%u6613%u8D2D%2Ca-sz-000998-%u9686%u5E73%u9AD8%u79D1; intellpositionL=1472.8px; intellpositionT=2214px; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; st_si=44692806308497; st_asi=delete; ASP.NET_SessionId=vqwpjm0zjmhdms1khwsx2sey; _qddaz=QD.x7conp.ccc1ye.kr50mpfc; EMFUND0=null; EMFUND1=07-08%2023%3A48%3A06@%23%24%u534E%u590F%u4EA7%u4E1A%u5347%u7EA7%u6DF7%u5408@%23%24005774; EMFUND2=07-08%2023%3A50%3A42@%23%24%u534E%u590F%u56FD%u4F01%u6539%u9769%u6DF7%u5408@%23%24001924; EMFUND3=07-12%2016%3A07%3A31@%23%24%u4FE1%u8FBE%u6FB3%u94F6%u65B0%u80FD%u6E90%u7CBE%u9009%u6DF7%u5408@%23%24012079; EMFUND4=07-14%2021%3A04%3A26@%23%24%u5E7F%u53D1%u4EF7%u503C%u4F18%u9009%u6DF7%u5408C@%23%24011135; EMFUND5=07-14%2015%3A28%3A21@%23%24%u8D22%u901A%u667A%u6167%u6210%u957F%u6DF7%u5408C@%23%24009063; EMFUND6=07-14%2021%3A03%3A52@%23%24%u534E%u590F%u5927%u76D8%u7CBE%u9009%u6DF7%u5408A@%23%24000011; EMFUND7=07-14%2021%3A13%3A00@%23%24%u5DE5%u94F6%u517B%u80012050%u6DF7%u5408%28FOF%29@%23%24006886; EMFUND8=07-15%2022%3A57%3A42@%23%24%u91D1%u9E70%u5185%u9700%u6210%u957F%u6DF7%u5408C@%23%24009969; EMFUND9=07-15 23:01:43@#$%u524D%u6D77%u5F00%u6E90%u6CAA%u6E2F%u6DF1%u6838%u5FC3%u8D44%u6E90%u6DF7%u5408A@%23%24003304; st_pvi=98760667666399; st_sp=2021-02-19%2012%3A00%3A58; st_inirUrl=http%3A%2F%2Fwww.zodiacn.ltd%2F; st_sn=6; st_psi=20210715230142577-112200305282-9987805961"
        tt_he = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
            "Cookie": tt_cookie,
            "Referer": "http: // fundf10.eastmoney.com /",
        }
        growth_rate = requests.get(url=r'http://fundgz.1234567.com.cn/js/' + fund + '.js', headers=tt_he)
        growth_rate = json.loads(growth_rate.text[8:-2])
        if growth_rate["gszzl"][0] == '-':
            fund_data = {"growth": growth_rate["gszzl"], "style": "card bg-success text-white shadow",
                         "name": growth_rate["name"]}
        else:
            fund_data = {"growth": growth_rate["gszzl"], "style": "card bg-danger text-white shadow",
                         "name": growth_rate["name"]}
        ret[fund] = fund_data
    return ret


def _linedata(fund_id):
    fund_dict = {}
    for id in range(0, 1):
        url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery183042533241398945254_1631367478759&fundCode=" + str(
            fund_id) + "&pageIndex=" + str(id) + "&pageSize=20&startDate=&endDate=&_=1631370992822"
        cookie = "em_hq_fls=js; qgqp_b_id=f32ae6d9951e87754f5f7e92b08e9583; st_si=34657268172654; st_asi=delete; HAList=a-sh-601128-%u5E38%u719F%u94F6%u884C%2Cd-hk-03968%2Cj-105-ACMR-ACM%20Research%20Inc-A%2Ca-sz-300750-%u5B81%u5FB7%u65F6%u4EE3%2Ca-sz-002409-%u96C5%u514B%u79D1%u6280%2Ca-sz-002508-%u8001%u677F%u7535%u5668%2Ca-sz-000725-%u4EAC%u4E1C%u65B9%uFF21%2Ca-sh-600519-%u8D35%u5DDE%u8305%u53F0%2Ca-sz-000858-%u4E94%20%u7CAE%20%u6DB2%2Ca-sz-002415-%u6D77%u5EB7%u5A01%u89C6%2Ca-sz-002812-%u6069%u6377%u80A1%u4EFD; EMFUND0=09-11%2015%3A47%3A46@%23%24%u5BCC%u56FD%u4E2D%u8BC1%u519B%u5DE5%u6307%u6570%28LOF%29A@%23%24161024; EMFUND1=09-11%2015%3A50%3A56@%23%24%u5BCC%u56FD%u5168%u7403%u79D1%u6280%u4E92%u8054%u7F51%28QDII%29@%23%24100055; EMFUND2=09-11%2015%3A57%3A18@%23%24%u534E%u590F%u6210%u957F%u6DF7%u5408@%23%24000001; EMFUND3=09-11%2016%3A02%3A15@%23%24%u4E1C%u65B9%u963F%u5C14%u6CD5%u4F18%u52BF%u4EA7%u4E1A%u6DF7%u5408A@%23%24009644; EMFUND4=09-11%2016%3A02%3A46@%23%24%u6613%u65B9%u8FBE%u84DD%u7B79%u7CBE%u9009%u6DF7%u5408@%23%24005827; EMFUND5=09-11%2019%3A27%3A24@%23%24%u5357%u65B9%u5B9D%u5143%u503A%u5238A@%23%24202101; EMFUND6=09-11%2017%3A09%3A10@%23%24%u5357%u65B9%u4E2D%u8BC1500ETF%u8054%u63A5A@%23%24160119; EMFUND7=09-11%2017%3A04%3A25@%23%24%u56FD%u6CF0%u4E2D%u8BC1%u7164%u70ADETF@%23%24515220; EMFUND8=09-11%2019%3A26%3A02@%23%24%u56FD%u8054%u5B89%u4FE1%u5FC3%u589E%u76CA%u503A%u5238@%23%24253030; EMFUND9=09-11 22:17:55@#$%u56FD%u6CF0CES%u534A%u5BFC%u4F53%u82AF%u7247%u884C%u4E1AETF%u8054%u63A5C@%23%24008282; st_pvi=62825606404183; st_sp=2021-09-09%2020%3A52%3A54; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Fs; st_sn=48; st_psi=20210911221751816-112200305282-7125850688"
        he = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
            "Cookie": cookie,
            "Referer": "http://fundf10.eastmoney.com/",
        }
        html = requests.get(url=url, headers=he)
        html.encoding = html.apparent_encoding
        gains = re.findall(r'L":"-*[0-9]+.[0-9]+"', html.text)
        gains = re.findall(r'-*[0-9]+.[0-9]+', str(gains))
        price = re.findall(r'"DWJZ":"[0-9]+.[0-9]+"', html.text)
        price = re.findall(r'[0-9]+.[0-9]+', str(price))
        date = re.findall(r'[0-9]+-[0-9]+-[0-9]+', html.text)
        gains = gains[::-1]
        price = price[::-1]
        date = date[::-1]
        for x, y, z in zip(date, price, gains):
            fund_dict[x] = (list((y, z)))
    return fund_dict  # {时间:[净值,涨幅]}


def _get_textvalue():
    tt_cookie = "qgqp_b_id=7110e64f9def8a6d6521b2453aff65fa; em_hq_fls=js; intellpositionL=1472.8px; intellpositionT=2214px; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; em-quote-version=topspeed; HAList=a-sh-601728-N%u7535%u4FE1%2Ca-sz-300782-%u5353%u80DC%u5FAE%2Ca-sh-603501-%u97E6%u5C14%u80A1%u4EFD%2Ca-sh-603986-%u5146%u6613%u521B%u65B0%2Ca-sz-300661-%u5723%u90A6%u80A1%u4EFD%2Cd-hk-01211%2Ca-sz-300014-%u4EBF%u7EAC%u9502%u80FD%2Ca-sh-603659-%u749E%u6CF0%u6765%2Ca-sz-300750-%u5B81%u5FB7%u65F6%u4EE3%2Ca-sh-603811-%u8BDA%u610F%u836F%u4E1A%2Ca-sz-300408-%u4E09%u73AF%u96C6%u56E2%2Cd-hk-00700; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; st_si=95391201505798; st_asi=delete; EMFUND0=null; EMFUND8=01-31%2010%3A55%3A40@%23%24%u56FD%u6CF0800%u6C7D%u8F66%u4E0E%u96F6%u90E8%u4EF6ETF%u8054%u63A5A@%23%24012973; EMFUND9=01-31 10:56:00@#$%u82F1%u5927%u56FD%u4F01%u6539%u9769%u4E3B%u9898%u80A1%u7968@%23%24001678; st_pvi=98760667666399; st_sp=2021-02-19%2012%3A00%3A58; st_inirUrl=http%3A%2F%2Fwww.zodiacn.ltd%2F; st_sn=16; st_psi=20230131111551181-119101302131-0498410301"
    tt_he = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70",
        "Cookie": tt_cookie,
        "Referer": "https://caifuhao.eastmoney.com/",
    }
    html = requests.get(
        url=r'https://caifuhaoapi.eastmoney.com/api/v1/webchannel/Article/GetAuthorNewList?authorid=125612&pagesize=10&pageindex=1&callback=jQuery18305579618504588668_1675134968001&businessid=0.11597124106753243&_=1675134969805',
        headers=tt_he)
    result = re.findall(r'"Result":\[{.*\],', html.text)
    news = re.findall(r'"ArtCode":"[0-9]*"', result[0])
    for new in news:
        id = re.findall(r'\d', new)
        id = "".join(id)
        html = requests.get(url=r'https://caifuhao.eastmoney.com/news/{}'.format(str(id)), headers=tt_he)
        temp = BeautifulSoup(html.text, "lxml")
        if temp.find_all('p')[:-3]:
            if temp.find_all('p')[:-3][0].string != " " and temp.find_all('p')[:-3][0].string != None:
                break
    value = ""
    for i in temp.find_all('p')[:-3]:
        if i.string:
            value += (i.string)
        else:
            def dfs(i):
                idir = dir(i)
                if "contents" not in idir:
                    return i
                value = ""
                for ii in i.contents:
                    value += dfs(ii)
                return value

            value += dfs(i)
    return value


class fund_db(object):
    @staticmethod
    def db():
        db = pymysql.connect(host=DB_IPADDRESS, user="root", passwd=DB_PASSWORD, database="fund",
                             cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        return db, cursor


class main(View, fund_db):
    def _config(self):
        db, cursor = self.db()
        sql = "select config  from config_table"
        cursor.execute(sql)
        config = cursor.fetchall()
        config = json.loads(config[0]["config"])
        m, date, money = config['m'], config["date"][0] + ':' + config["date"][1], str(int(config["money"]) * 4)
        now_money = 0
        id_list = ["004746", "013291", "008888", "013048"]
        for i in id_list:
            sql_hold = "select hold from fund_inf where fund_id={} and ch_name='z_record'".format(i)
            cursor.execute(sql_hold)
            hold = cursor.fetchall()
            hold_int = int(hold[0]["hold"])
            sql_week = "select sum(cr_change) from week_journal where fund_id={}".format(i)
            cursor.execute(sql_week)
            hold_week = cursor.fetchall()
            if not hold_week[0]["sum(cr_change)"]:
                hold_week[0]["sum(cr_change)"] = "0"
            hold_int += int(hold_week[0]["sum(cr_change)"])
            tt_cookie = "qgqp_b_id=7110e64f9def8a6d6521b2453aff65fa; em_hq_fls=js; HAList=a-sh-600760-%u4E2D%u822A%u6C88%u98DE%2Ca-sz-002024-%u82CF%u5B81%u6613%u8D2D%2Ca-sz-000998-%u9686%u5E73%u9AD8%u79D1; intellpositionL=1472.8px; intellpositionT=2214px; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; st_si=44692806308497; st_asi=delete; ASP.NET_SessionId=vqwpjm0zjmhdms1khwsx2sey; _qddaz=QD.x7conp.ccc1ye.kr50mpfc; EMFUND0=null; EMFUND1=07-08%2023%3A48%3A06@%23%24%u534E%u590F%u4EA7%u4E1A%u5347%u7EA7%u6DF7%u5408@%23%24005774; EMFUND2=07-08%2023%3A50%3A42@%23%24%u534E%u590F%u56FD%u4F01%u6539%u9769%u6DF7%u5408@%23%24001924; EMFUND3=07-12%2016%3A07%3A31@%23%24%u4FE1%u8FBE%u6FB3%u94F6%u65B0%u80FD%u6E90%u7CBE%u9009%u6DF7%u5408@%23%24012079; EMFUND4=07-14%2021%3A04%3A26@%23%24%u5E7F%u53D1%u4EF7%u503C%u4F18%u9009%u6DF7%u5408C@%23%24011135; EMFUND5=07-14%2015%3A28%3A21@%23%24%u8D22%u901A%u667A%u6167%u6210%u957F%u6DF7%u5408C@%23%24009063; EMFUND6=07-14%2021%3A03%3A52@%23%24%u534E%u590F%u5927%u76D8%u7CBE%u9009%u6DF7%u5408A@%23%24000011; EMFUND7=07-14%2021%3A13%3A00@%23%24%u5DE5%u94F6%u517B%u80012050%u6DF7%u5408%28FOF%29@%23%24006886; EMFUND8=07-15%2022%3A57%3A42@%23%24%u91D1%u9E70%u5185%u9700%u6210%u957F%u6DF7%u5408C@%23%24009969; EMFUND9=07-15 23:01:43@#$%u524D%u6D77%u5F00%u6E90%u6CAA%u6E2F%u6DF1%u6838%u5FC3%u8D44%u6E90%u6DF7%u5408A@%23%24003304; st_pvi=98760667666399; st_sp=2021-02-19%2012%3A00%3A58; st_inirUrl=http%3A%2F%2Fwww.zodiacn.ltd%2F; st_sn=6; st_psi=20210715230142577-112200305282-9987805961"
            tt_he = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
                "Cookie": tt_cookie,
                "Referer": "http: // fundf10.eastmoney.com /",
            }
            worth = requests.get(url=r'http://fundgz.1234567.com.cn/js/' + i + '.js', headers=tt_he)
            worth = re.findall(r'"gsz":"[0-9]+.[0-9]+"', worth.text)
            worth = float(re.findall(r'[0-9]+.[0-9]+', str(worth))[0])
            now_money += int(worth * hold_int)
        db.close()
        return m, date, money, now_money

    def _pie_chart(self):
        db, cursor = self.db()
        id_list = ["004746", "013291", "008888", "013048"]
        hold_num = []
        for i in id_list:
            sql_hold = "select hold from fund_inf where fund_id={} and ch_name='z_record'".format(i)
            cursor.execute(sql_hold)
            hold = cursor.fetchall()
            hold_int = int(hold[0]["hold"])
            sql_week = "select sum(cr_change) from week_journal where fund_id={} and ch_name='z_record'".format(i)
            cursor.execute(sql_week)
            hold_week = cursor.fetchall()
            if not hold_week[0]["sum(cr_change)"]:
                hold_week[0]["sum(cr_change)"] = "0"
            hold_num.append(int(hold_week[0]["sum(cr_change)"]) + hold_int)
        db.close()
        hold_name = ["易方达上证50", "富国沪深300", "华夏国证半导体芯片", "富国中证新能源汽车"]
        return hold_name, hold_num

    def _line_chart(self, cookie_date):
        db, cursor = self.db()
        id_list = ["004746", "013291", "008888", "013048"]
        daydict = {}
        for id in id_list:
            t = time.strftime("%Y-%m-%d")
            new_date = time.mktime(time.strptime(t, "%Y-%m-%d"))
            if not cookie_date or cookie_date != str(new_date):
                print(id, "更新")
                try:
                    sql = "DELETE FROM day_{}".format(id)
                    cursor.execute(sql)
                    db.commit()
                    linedata = _linedata(id)
                    keylist = list(linedata.keys())
                    for i in keylist[len(keylist):len(keylist) - 8:-1]:
                        sql = "INSERT INTO day_{}(date,value)VALUES ('{}','{}')".format(id, i, linedata[i][1])
                        cursor.execute(sql)
                        db.commit()
                except:
                    db.rollback()
            sql = "select date,value from day_{}".format(id)
            cursor.execute(sql)
            daydata = cursor.fetchall()
            daydict[id] = daydata
        db.close()
        date7, value008888, value004746, value013291, value013048 = [], [], [], [], []
        for x, y, z, r in zip(daydict["008888"], daydict["004746"], daydict["013291"], daydict["013048"]):
            date7.append(x["date"])
            value008888.append(x["value"])
            value004746.append(y["value"])
            value013291.append(z["value"])
            value013048.append(r["value"])
        date7, value008888, value004746, value013291, value013048 = date7[::-1], value008888[::-1], value004746[
                                                                                                    ::-1], value013291[
                                                                                                           ::-1], value013048[
                                                                                                                  ::-1]
        return date7, value008888, value004746, value013291, value013048

    def get(self, request):
        user = request.COOKIES.get("user")
        cookie_date = request.COOKIES.get("new_date")
        m, date, money, now_money = self._config()
        hold_name, hold_num = self._pie_chart()
        date7, value008888, value004746, value013291, value013048 = self._line_chart(cookie_date)
        textvalue = _get_textvalue()
        fund_floatings = _fund_floating()
        ret = render(request, "index.html",
                     {"user": user,
                      'm': m, "date": date, "money": money, "now_money": now_money,
                      "hold_name": hold_name, "hold_num": hold_num,
                      "date7": date7, "value013291": value013291, "value013048": value013048,
                      "value004746": value004746, "value008888": value008888,
                      "textvalue": textvalue,
                      "fund_floatings": fund_floatings,
                      })
        ret.set_cookie("m", m), ret.set_cookie("date", date), ret.set_cookie("money", money), ret.set_cookie(
            "now_money", now_money)
        t = time.strftime("%Y-%m-%d")
        new_date = time.mktime(time.strptime(t, "%Y-%m-%d"))
        ret.set_cookie("new_date", new_date, expires=60 * 60 * 24)
        return ret


class config(View, fund_db):
    def _up_cofig(self, m, date, money):
        db, cursor = self.db()
        sql = "select config from config_table"
        cursor.execute(sql)
        config = cursor.fetchall()
        config = json.loads(config[0]["config"])
        # 修订config数据处
        config["m"], config["date"], config["money"] = m, date, money
        config = json.dumps(config)
        sql = "update config_table set config='{}' where id=1".format(config)
        cursor.execute(sql)
        db.commit()
        db.close()
        fund_main_app.web_socket.main("reboot")

    def get(self, request):
        m, date, money, now_money = request.COOKIES.get('m'), request.COOKIES.get('date'), request.COOKIES.get(
            'money'), request.COOKIES.get('now_money')
        user = request.COOKIES.get("user")
        new = datetime.datetime.now().date()
        if not is_workday(new) or (time.localtime().tm_hour >= 22 or time.localtime().tm_hour <= 13) or (
                time.localtime().tm_hour == 14 and time.localtime().tm_min < 50):
            if not m:
                m, date, money, now_money = "5", "14:55", "4000", "****"
            return render(request, "config.html", {
                "m": m, "date": date, "money": money, "now_money": now_money,
                "user": user,
            })
        else:
            return redirect("error")

    def post(self, request):
        m, date, money = request.POST.get("m"), request.POST.get("date"), int(request.POST.get("money")) // 4
        date = date.split(":")
        self._up_cofig(m, date, money)
        return redirect("index")


class week_data(View, fund_db):
    def _select_data(self):
        db, cursor = self.db()
        sql = "select * from week_journal"
        cursor.execute(sql)
        week_journal = cursor.fetchall()
        for i in week_journal:
            i["cr_date"] = datetime.datetime.strftime(i["cr_date"], '%Y-%m-%d %H:%M:%S')
        return week_journal

    def get(self, request):
        week_journal = self._select_data()
        user = request.COOKIES.get("user")
        return render(request, "data_list.html", {
            "journal": week_journal,
            "user": user,
            "table_name": "week_journal",
        })


class Paginator(object):
    def __init__(self, data_list, pag):
        self.data_list = []
        self.sumnum = len(data_list)
        s = len(data_list)
        for i in range(0, s, pag):
            self.data_list.append(data_list[i:i + pag if i + pag < s else s])

    def get_page(self, page):
        return self.data_list[page]

    def get_sum_page(self):
        sum_page = [i + 1 for i in range(len(self.data_list))]
        return sum_page

    def get_sumnum(self):
        return self.sumnum


class sum_data(View, fund_db):
    def _select_data(self, pag=0):
        db, cursor = self.db()
        sql = "select * from sum_journal ORDER BY id DESC LIMIT 100"
        cursor.execute(sql)
        sum_journal = cursor.fetchall()
        for i in sum_journal:
            i["cr_date"] = datetime.datetime.strftime(i["cr_date"], '%Y-%m-%d %H:%M:%S')
        paginator = Paginator(sum_journal, 10)
        deal_list = paginator.get_page(pag)
        sum_page = paginator.get_sum_page()
        sumnum = paginator.get_sumnum()
        return deal_list, sum_page, sumnum

    def get(self, request):
        pag = request.GET.get("pag", 0)
        if pag != 0: pag = int(pag) - 1
        sum_journal, sum_page, sumnum = self._select_data(pag)
        user = request.COOKIES.get("user")
        return render(request, "data_list.html", {
            "journal": sum_journal,
            "user": user,
            "table_name": "sum_journal",
            "sum_page": sum_page,
            "sumnum": sumnum,
            "start_page": pag * 10,
            "end_page": len(sum_journal) + pag * 10 - 1,
        })


class delete(View, fund_db):
    def get(self, request, dele_obj, pk):
        db, cursor = self.db()
        sql = "delete from {} where id={}".format(dele_obj, pk)
        cursor.execute(sql)
        db.commit()
        db.close()
        return JsonResponse({"status": 200})


class fund_inf(View, fund_db):
    def _inf(self):
        db, cursor = self.db()
        sql = "select * from fund_inf"
        cursor.execute(sql)
        inf_data = cursor.fetchall()
        return inf_data

    def get(self, request):
        inf_data = self._inf()
        user = request.COOKIES.get("user")
        return render(request, "fund_inf.html", {
            "inf_data": inf_data,
            "user": user,
        })


class updata(View, fund_db):
    def get(self, request, updata_obj, pk):
        value = "hold"
        if updata_obj != "fund_inf":
            value = "cr_change"
        db, cursor = self.db()
        updata = request.GET.get("updata")
        sql = "update {} set {}={} where id={}".format(updata_obj, value, updata, pk)
        cursor.execute(sql)
        db.commit()
        db.close()
        return JsonResponse({"status": 200})


class login(View, fund_db):
    def get(self, request):
        return render(request, "login.html", {"color": "form-control"})

    def post(self, request):
        user = request.POST.get("user")
        password = request.POST.get("password")
        password_obj = hashlib.sha256()
        password_obj.update(password.encode("utf-8"))
        password_sha = password_obj.hexdigest()
        db, cursor = self.db()
        sql = "select password from login where user='{}'".format(user)
        cursor.execute(sql)
        password_db = cursor.fetchall()
        if len(password_db) != 0 and (password_sha == password_db[0]["password"]):
            ret = redirect("index")
            user_obj = hashlib.sha256()
            user_obj.update(user.encode("utf-8"))
            login_status = user_obj.hexdigest()
            ret.set_cookie("login_status", login_status, expires=60 * 60 * 24)
            request.session[login_status] = login_status
            ret.set_cookie("user", user)
            return ret
        else:
            return render(request, "login.html", {"color": "form-control-red", "err": "账号密码错误"})


class FundFloatSet(View, fund_db):
    def get(self, request):
        return render(request, "fund_float_set.html")


class error(View):
    def get(self, request):
        return render(request, "error.html")
