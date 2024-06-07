# -*- coding: utf-8 -*-
from datetime import datetime

import bs4
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
def _linedata(fund_id):  # 15天业绩走势
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
        fund_data = json.loads(fund_data)[0:15]
        for day_info in fund_data[::-1]:
            if not day_info["JZZZL"]: day_info["JZZZL"] = 0
            fund_dict[day_info["FSRQ"]] = [day_info["DWJZ"], day_info["JZZZL"]]
    return fund_dict


def _get_textvalue():
    """
    获取基金最新信息
    """
    tt_cookie = "qgqp_b_id=6aa0da45630bb940299f68d1cd827ded; HAList=ty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-90-BK0896-%u767D%u9152%2Cty-100-KSE100-%u5DF4%u57FA%u65AF%u5766%u5361%u62C9%u5947%2Cty-1-000300-%u6CAA%u6DF1300%2Cty-100-SENSEX-%u5370%u5EA6%u5B5F%u4E70SENSEX%2Cty-100-ICEXI-%u51B0%u5C9BICEX%2Cty-100-CSEALL-%u65AF%u91CC%u5170%u5361%u79D1%u4F26%u5761%2Cty-155-77OR-REPUBLIC%20OF%20GHANA%20%28THE%29%206.375; st_si=14445956617934; st_asi=delete; st_pvi=61521603029306; st_sp=2023-10-24%2009%3A53%3A57; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=5; st_psi=20240412105047684-1190142302762-2842893775"
    tt_he = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "Cookie": tt_cookie,
        "Referer": "https://finance.eastmoney.com/a/202404123041563494.html",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }
    html = requests.get(
        url=r'https://finance.eastmoney.com/',
        headers=tt_he)

    html.encoding = 'gb2312'
    soup = bs4.BeautifulSoup(html.text, 'lxml')
    test = soup.find_all("div", class_="content mt0")

    news = []
    for href in test[0].find_all("a"):
        news.append(href['href'])

    for new_url in news:
        html = requests.get(url=new_url, headers=tt_he)
        temp = BeautifulSoup(html.text, "lxml")
        if temp.find_all('p')[:-3]:
            if temp.find_all('p')[:-3][0].string != " " and temp.find_all('p')[:-3][0].string != None:
                break
    value = ""
    for i in temp.find_all('p')[:-3]:
        abandoned = ["方便，快捷", "手机查看财经快讯", "专业，丰富", "一手掌握市场脉搏", "提示：", "微信扫一扫",
                     "分享到您的", "朋友圈"]

        if i.string:
            if i.string.strip() in abandoned: continue
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
        15天业绩走势
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
                if len(date_list) != 15:
                    date_list.append(datetime.strftime(day_info["date"], '%Y-%m-%d'))
                res[abbr].append(({"profit_loss": day_info["profit_loss"]}))
        db.close()
        return res, date_list

    @staticmethod
    def _hotspot():
        """
        获取热门板块
        :return: res[{浮动盈亏，名称}]
        """
        tt_cookie = "qgqp_b_id=6aa0da45630bb940299f68d1cd827ded; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; HAList=ty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-1-000300-%u6CAA%u6DF1300%2Cty-100-SENSEX-%u5370%u5EA6%u5B5F%u4E70SENSEX%2Cty-100-ICEXI-%u51B0%u5C9BICEX%2Cty-100-CSEALL-%u65AF%u91CC%u5170%u5361%u79D1%u4F26%u5761%2Cty-100-KSE100-%u5DF4%u57FA%u65AF%u5766%u5361%u62C9%u5947%2Cty-155-77OR-REPUBLIC%20OF%20GHANA%20%28THE%29%206.375; EMFUND0=null; EMFUND8=01-25%2011%3A45%3A18@%23%24%u534E%u590F%u56FD%u8BC1%u534A%u5BFC%u4F53%u82AF%u7247ETF%u8054%u63A5C@%23%24008888; EMFUND9=02-01 13:59:50@#$%u534E%u590F%u667A%u80DC%u5148%u950B%u80A1%u7968C@%23%24014198; st_si=55013451928066; st_asi=delete; st_pvi=61521603029306; st_sp=2023-10-24%2009%3A53%3A57; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=5; st_psi=20240226110026222-113200301831-1217984057"
        tt_he = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            "Cookie": tt_cookie,
            "Referer": "https://quote.eastmoney.com/zhuti/?from=center",
        }
        worth = requests.get(url=r'https://quote.eastmoney.com/zhuti/api/todayopportunity', headers=tt_he)

        worth_dict = json.loads(worth.text)
        res = []

        for data_dict in worth_dict["result"][0]["Data"]:
            data_list = data_dict.split('|')
            res.append({
                "profit_loss": data_list[0],
                "name": data_list[2]
            })

        return res

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

    @staticmethod
    def _turnover():
        """
        获取当日A股成交量
        :return: 成交量
        """
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?cb=jQuery11230955998691743706_1717559609224&fltt=2&secids=1.000001%2C0.399001&fields=f1%2Cf2%2Cf3%2Cf4%2Cf6%2Cf12%2Cf13%2Cf104%2Cf105%2Cf106&ut=b2884a393a59ad64002292a3e90d46a5&_=1717559609225"
        tt_cookie = "qgqp_b_id=f6373a3738190ff68c502da24e38db83; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND0=null; EMFUND6=05-15%2010%3A42%3A26@%23%24%u534E%u590F%u667A%u80DC%u5148%u950B%u80A1%u7968C@%23%24014198; EMFUND7=05-14%2010%3A14%3A35@%23%24%u534E%u590F%u4E2D%u8BC1%u52A8%u6F2B%u6E38%u620FETF%u8054%u63A5A@%23%24012768; EMFUND8=05-15%2010%3A40%3A41@%23%24%u62DB%u5546%u4F53%u80B2%u6587%u5316%u4F11%u95F2%u80A1%u7968C@%23%24015395; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; EMFUND9=05-20 14:21:06@#$%u534E%u590F%u56FD%u8BC1%u534A%u5BFC%u4F53%u82AF%u7247ETF%u8054%u63A5C@%23%24008888; emshistory=%5B%22%E5%8F%B0%E6%B9%BE%E6%8C%87%E6%95%B0%22%5D; st_si=11311620896037; has_jump_to_web=1; HAList=ty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-0-399001-%u6DF1%u8BC1%u6210%u6307%2Cty-1-000300-%u6CAA%u6DF1300%2Cty-0-002027-%u5206%u4F17%u4F20%u5A92%2Cty-100-KSE100-%u5DF4%u57FA%u65AF%u5766%u5361%u62C9%u5947%2Cty-100-TWII-%u53F0%u6E7E%u52A0%u6743%2Cty-0-002371-%u5317%u65B9%u534E%u521B%2Cty-0-002049-%u7D2B%u5149%u56FD%u5FAE%2Cty-1-603444-%u5409%u6BD4%u7279%2Cty-90-BK0896-%u767D%u9152; websitepoptg_api_time=1717493094477; st_pvi=61521603029306; st_sp=2023-10-24%2009%3A53%3A57; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=27; st_psi=20240605115249169-113300300871-7968356103; st_asi=delete"
        tt_he = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "Cookie": tt_cookie,
            "Referer": "https://data.eastmoney.com/zjlx/dpzjlx.html",
        }

        worth = requests.get(url=url, headers=tt_he)
        json_data = re.search(r'\((.*)\)', worth.text).group(1)
        worth_dict = json.loads(json_data)
        sum_num = 0
        for worth in worth_dict["data"]["diff"]:
            sum_num += worth["f6"]

        turnover_num = int(sum_num // 100000000)
        return turnover_num

    @staticmethod
    def _overall_situation():
        """
        获取上证、深证、成交量等数据
        :return:
        {
        shangz:上证指数,shangz_profit_loss:上证指数涨跌,shangz_class:主题
        shenz:深证指数,shenz_profit_loss:深证指数涨跌,shenz_class:主题
        turnover_num:成交量
        }
        """
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?cb=jQuery112303693369501585688_1717745045870&fltt=2&secids=1.000001%2C0.399001&fields=f1%2Cf2%2Cf3%2Cf4%2Cf6%2Cf12%2Cf13%2Cf104%2Cf105%2Cf106&ut=b2884a393a59ad64002292a3e90d46a5&_=1717745045872"
        tt_cookie = "qgqp_b_id=f6373a3738190ff68c502da24e38db83; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; emshistory=%5B%22%E5%8F%B0%E6%B9%BE%E6%8C%87%E6%95%B0%22%5D; st_si=11311620896037; has_jump_to_web=1; st_asi=delete; EMFUND0=null; EMFUND5=06-06%2011%3A04%3A44@%23%24%u534E%u590F%u667A%u80DC%u5148%u950B%u80A1%u7968C@%23%24014198; EMFUND6=05-14%2010%3A14%3A35@%23%24%u534E%u590F%u4E2D%u8BC1%u52A8%u6F2B%u6E38%u620FETF%u8054%u63A5A@%23%24012768; EMFUND7=05-15%2010%3A40%3A41@%23%24%u62DB%u5546%u4F53%u80B2%u6587%u5316%u4F11%u95F2%u80A1%u7968C@%23%24015395; EMFUND8=05-20%2014%3A21%3A06@%23%24%u534E%u590F%u56FD%u8BC1%u534A%u5BFC%u4F53%u82AF%u7247ETF%u8054%u63A5C@%23%24008888; EMFUND9=06-06 11:17:46@#$%u534E%u590F%u5B89%u6CF0%u5BF9%u51B2%u7B56%u75653%u4E2A%u6708%u5B9A%u5F00%u6DF7%u5408@%23%24008856; HAList=ty-0-399401-%u4E2D%u5C0F%u76D8%2Cty-1-688325-%u8D5B%u5FAE%u5FAE%u7535%2Cty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-0-399001-%u6DF1%u8BC1%u6210%u6307%2Cty-1-000300-%u6CAA%u6DF1300%2Cty-0-002027-%u5206%u4F17%u4F20%u5A92%2Cty-100-KSE100-%u5DF4%u57FA%u65AF%u5766%u5361%u62C9%u5947%2Cty-100-TWII-%u53F0%u6E7E%u52A0%u6743%2Cty-0-002371-%u5317%u65B9%u534E%u521B%2Cty-0-002049-%u7D2B%u5149%u56FD%u5FAE; st_pvi=61521603029306; st_sp=2023-10-24%2009%3A53%3A57; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=54; st_psi=20240607152241752-113300300871-5429805951"
        tt_he = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "Cookie": tt_cookie,
            "Referer": "https://data.eastmoney.com/zjlx/dpzjlx.html",
        }

        worth = requests.get(url=url, headers=tt_he)
        json_data = re.search(r'\((.*)\)', worth.text).group(1)
        json_data = json.loads(json_data)
        turnover_num = int((json_data["data"]["diff"][0]["f6"] + json_data["data"]["diff"][1]["f6"]) // 100000000)
        shangz = json_data["data"]["diff"][0]["f2"]
        shangz_profit_loss = json_data["data"]["diff"][0]["f3"]
        shenz = json_data["data"]["diff"][1]["f2"]
        shenz_profit_loss = json_data["data"]["diff"][1]["f3"]
        ret = {
            "shangz": shangz,
            "shangz_profit_loss": shangz_profit_loss,
            "shangz_class": "card bg-danger text-white shadow" if shangz_profit_loss >= 0 else "card bg-success text-white shadow",
            "shenz": shenz,
            "shenz_profit_loss": shenz_profit_loss,
            "shenz_class": "card bg-danger text-white shadow" if shenz_profit_loss >= 0 else "card bg-success text-white shadow",
            "turnover_num": turnover_num,
        }
        return ret

    def get(self, request):
        user = request.COOKIES.get("user")
        cookie_date = request.COOKIES.get("new_date")
        m, date, money, now_money = self._config()  # 基金概括
        hold_name, hold_num = self._pie_chart()  # 持仓比例
        date7, date_list = self._line_chart(cookie_date)  # 15天业绩走势
        textvalue, new_url = _get_textvalue()  # 最新消息
        fund_floatings = self._fund_floating()  # 基金涨幅
        inform_obj = Inform()
        inform_dict = inform_obj.data()  # 消息通知
        overall_situation = self._overall_situation()  # 大盘涨幅
        ret = render(request, "index.html",
                     {"user": user,
                      'm': m, "date": date, "money": money, "now_money": now_money,
                      "hold": zip(hold_name, hold_num), "hold_name": hold_name,
                      "date7": date7, "date_list": date_list,
                      "textvalue": textvalue, "new_url": new_url,
                      "fund_floatings": fund_floatings,
                      "inform_dict": inform_dict,
                      "overall_situation": overall_situation,
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
