# -*- coding: utf-8 -*-
from datetime import datetime

from django.shortcuts import render
import pymysql
import json
import re
import requests
from django.views import View
import time
from bs4 import BeautifulSoup

from fund_web.settings import DB_PASSWORD, DB_IPADDRESS, PORT


# Create your views here.
def _linedata(fund_id):  # 7天业绩走势
    """
    :param fund_id: 基金编号
    :return: {时间:[净值,涨幅]}
    """
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
        fund_data = re.findall(r'\[.*\]', html.text)[0]
        fund_data = json.loads(fund_data)[0:7]
        for day_info in fund_data[::-1]:
            if not day_info["JZZZL"]: day_info["JZZZL"] = 0
            fund_dict[day_info["FSRQ"]] = [day_info["DWJZ"], day_info["JZZZL"]]
    return fund_dict


def _get_textvalue():
    """
    获取基金最新信息
    """
    tt_cookie = "qgqp_b_id=7110e64f9def8a6d6521b2453aff65fa; em_hq_fls=js; intellpositionL=1472.8px; intellpositionT=2214px; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; em-quote-version=topspeed; HAList=a-sh-601728-N%u7535%u4FE1%2Ca-sz-300782-%u5353%u80DC%u5FAE%2Ca-sh-603501-%u97E6%u5C14%u80A1%u4EFD%2Ca-sh-603986-%u5146%u6613%u521B%u65B0%2Ca-sz-300661-%u5723%u90A6%u80A1%u4EFD%2Cd-hk-01211%2Ca-sz-300014-%u4EBF%u7EAC%u9502%u80FD%2Ca-sh-603659-%u749E%u6CF0%u6765%2Ca-sz-300750-%u5B81%u5FB7%u65F6%u4EE3%2Ca-sh-603811-%u8BDA%u610F%u836F%u4E1A%2Ca-sz-300408-%u4E09%u73AF%u96C6%u56E2%2Cd-hk-00700; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; st_si=95391201505798; st_asi=delete; EMFUND0=null; EMFUND8=01-31%2010%3A55%3A40@%23%24%u56FD%u6CF0800%u6C7D%u8F66%u4E0E%u96F6%u90E8%u4EF6ETF%u8054%u63A5A@%23%24012973; EMFUND9=01-31 10:56:00@#$%u82F1%u5927%u56FD%u4F01%u6539%u9769%u4E3B%u9898%u80A1%u7968@%23%24001678; st_pvi=98760667666399; st_sp=2021-02-19%2012%3A00%3A58; st_inirUrl=http%3A%2F%2Fwww.zodiacn.ltd%2F; st_sn=16; st_psi=20230131111551181-119101302131-0498410301"
    tt_he = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70",
        "Cookie": tt_cookie,
        "Referer": "https://caifuhao.eastmoney.com/",
    }
    html = requests.get(
        url=r'https://i.eastmoney.com/api/guba/userdynamiclistv2?uid=6082094936906114&pagenum=1&pagesize=10&type=1&_=1694426400455',
        headers=tt_he)
    text = json.loads(html.text)
    news = []
    new_url = ''
    for text_url in text["result"]:
        news.append(text_url["extend"]["ArtCode"])
    for new in news:
        id = re.findall(r'\d', new)
        id = "".join(id)
        new_url = r'https://caifuhao.eastmoney.com/news/{}'.format(str(id))
        html = requests.get(url=new_url, headers=tt_he)
        temp = BeautifulSoup(html.text, "lxml")
        if temp.find_all('p')[:-3]:
            if temp.find_all('p')[:-3][0].string != " " and temp.find_all('p')[:-3][0].string != None:
                break
    value = ""
    for i in temp.find_all('p')[:-3]:
        if i.string:
            value += (i.string.strip())
        else:
            def dfs(i):
                idir = dir(i)
                if "contents" not in idir:
                    return i
                value = ""
                for ii in i.contents:
                    value += dfs(ii).strip()
                return value

            value += dfs(i)

    if value == "":
        value = "暂无新消息"
    else:
        value = value[:1100] + "..."

    return value, new_url


class FundDb(object):
    """
    数据库object
    """

    @staticmethod
    def db():
        """
        数据库连接
        :return:db, cursor
        """
        db = pymysql.connect(host=DB_IPADDRESS, user="root", passwd=DB_PASSWORD, database="fund",
                             cursorclass=pymysql.cursors.DictCursor, port=PORT)
        cursor = db.cursor()
        return db, cursor

    def _fund_id_list(self):
        """
        获取基金id
        """
        db, cursor = self.db()
        sql = "SELECT fund_id,name,abbr FROM fund_inf;"
        cursor.execute(sql)
        fund_list = cursor.fetchall()
        id_list = [fund_id["fund_id"] for fund_id in fund_list]
        name_list = [fund_name["name"].replace("\t", "") for fund_name in fund_list]
        abbr_list = [fund_name["abbr"].replace("\t", "") for fund_name in fund_list]
        return id_list, name_list, abbr_list


class Inform(FundDb):
    """
    信息通知
    """

    def data(self):
        """
        信息数据
        """
        db, cursor = self.db()
        fund_id_list, fun_name_list, _ = self._fund_id_list()
        res = {}
        for fund_id, fund_name in zip(fund_id_list, fun_name_list):
            sql = "SELECT profit_loss,date FROM seven_days_profit_loss WHERE fund_id={} ORDER BY id DESC LIMIT 1;".format(
                fund_id)
            cursor.execute(sql)
            profit_loss = cursor.fetchall()
            if not profit_loss: continue
            date = datetime.strftime(profit_loss[0]["date"], '%Y-%m-%d')
            res[fund_id] = {"name": fund_name,
                            "profit_loss": profit_loss[0]["profit_loss"],
                            "date": date}
        return res


class Home(View, FundDb):
    """
    数据大屏
    """

    def _config(self):
        """
        基金概括
        :return:m(倍率), date(时间), money(预定金额), now_money(实际金额)
        """
        db, cursor = self.db()
        sql = "select config  from config_table"
        cursor.execute(sql)
        config = cursor.fetchall()
        config = json.loads(config[0]["config"])
        date = config["date"][0] + ':' + config["date"][1]
        now_money = 0
        money = 0
        sql = "SELECT fund_id,reserve_money,rate FROM fund_inf"
        cursor.execute(sql)
        fund_id_list = cursor.fetchall()
        id_list = [fund_id["fund_id"] for fund_id in fund_id_list]
        m = fund_id_list[0]["rate"]
        for fund in fund_id_list:
            money += fund["reserve_money"]
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
        """
        持仓比例(饼图)
        :return:hold_name(持仓基金名称), hold_num（持仓基金仓位）
        """
        db, cursor = self.db()
        id_list, _, hold_name = self._fund_id_list()
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
        return hold_name, hold_num

    def _line_chart(self, cookie_date):
        """
        7天业绩走势
        :param cookie_date:上次更新时间
        :return: res(持仓基金7天的涨幅), date_list(7天的日期)
        """
        db, cursor = self.db()
        id_list, _, abbr_list = self._fund_id_list()
        res = {}
        date_list = []
        for id, abbr in zip(id_list, abbr_list):
            t = time.strftime("%Y-%m-%d")
            new_date = time.mktime(time.strptime(t, "%Y-%m-%d"))
            if not cookie_date or cookie_date != str(new_date):
                print(id, "更新")
                try:
                    sql = "DELETE FROM seven_days_profit_loss WHERE fund_id={};".format(id)
                    cursor.execute(sql)
                    db.commit()
                    linedata = _linedata(id)
                    for i in linedata.keys():
                        sql = "INSERT INTO seven_days_profit_loss(fund_id,date,profit_loss)VALUES ('{}','{}','{}')".format(
                            id, i, linedata[i][1])
                        cursor.execute(sql)
                        db.commit()
                except:
                    db.rollback()
            sql = "select date,profit_loss from seven_days_profit_loss where fund_id={}".format(id)
            cursor.execute(sql)
            daydata = cursor.fetchall()
            res[abbr] = []
            for day_info in daydata:
                if len(date_list) != 7:
                    date_list.append(datetime.strftime(day_info["date"], '%Y-%m-%d'))
                res[abbr].append(({"profit_loss": day_info["profit_loss"]}))
        db.close()
        return res, date_list

    def _fund_floating(self):
        """
        获取基金涨幅
        :return: ret(基金实时涨幅情况)
        """
        fund_list = []
        db, cursor = self.db()
        sql = """select fund_id from new_fund_Increase;"""
        cursor.execute(sql)
        for fund_obj in cursor.fetchall():
            for fund_id in fund_obj.values():
                fund_list.append(fund_id)
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

    def get(self, request):
        user = request.COOKIES.get("user")
        cookie_date = request.COOKIES.get("new_date")
        m, date, money, now_money = self._config()  # 基金概括
        hold_name, hold_num = self._pie_chart()  # 持仓比例
        date7, date_list = self._line_chart(cookie_date)  # 7天业绩走势
        textvalue, new_url = _get_textvalue()  # 最新消息
        fund_floatings = self._fund_floating()  # 基金涨幅
        inform_obj = Inform()
        inform_dict = inform_obj.data()  # 消息通知
        ret = render(request, "index.html",
                     {"user": user,
                      'm': m, "date": date, "money": money, "now_money": now_money,
                      "hold": zip(hold_name, hold_num), "hold_name": hold_name,
                      "date7": date7, "date_list": date_list,
                      "textvalue": textvalue, "new_url": new_url,
                      "fund_floatings": fund_floatings,
                      "inform_dict": inform_dict,
                      })
        ret.set_cookie("m", m), ret.set_cookie("date", date), ret.set_cookie("money", money), ret.set_cookie(
            "now_money", now_money)
        t = time.strftime("%Y-%m-%d")
        new_date = time.mktime(time.strptime(t, "%Y-%m-%d"))
        ret.set_cookie("new_date", new_date, expires=60 * 60 * 24)
        return ret


class Error(View):  # 404
    @staticmethod
    def get(request):
        user = request.COOKIES.get("user")
        inform_obj = Inform()
        inform_dict = inform_obj.data()  # 消息通知
        return render(request, "error.html", {"user": user, "inform_dict": inform_dict})
