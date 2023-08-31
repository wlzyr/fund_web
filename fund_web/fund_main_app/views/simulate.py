import json
import re

import pymysql
import requests
from django.shortcuts import render, redirect
import importlib
from django.views import View

from fund_web.settings import DB_IPADDRESS, DB_PASSWORD, PORT
from fund_main_app.views import data as data
from views.bi import Inform


class FundDb(object):  # 数据库object
    @staticmethod
    def db():
        db = pymysql.connect(host=DB_IPADDRESS, user="root", passwd=DB_PASSWORD, database="fund",
                             cursorclass=pymysql.cursors.DictCursor, port=PORT)
        cursor = db.cursor()
        return db, cursor


class fund_date(object):  # 策略模拟数据
    def __init__(self, fund_id, date_type):
        self.fund_id = fund_id
        if date_type == '1':
            self.star = 1
        elif date_type == '2':
            self.star = 6
        else:
            self.star = 12

    def date(self):
        fund_dict = {}
        for id in range(self.star, 0, -1):  # 19, 0, -1
            url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery183042533241398945254_1631367478759&fundCode=" + str(
                self.fund_id) + "&pageIndex=" + str(id) + "&pageSize=20&startDate=&endDate=&_=1631370992822"
            cookie = "em_hq_fls=js; qgqp_b_id=f32ae6d9951e87754f5f7e92b08e9583; st_si=34657268172654; st_asi=delete; HAList=a-sh-601128-%u5E38%u719F%u94F6%u884C%2Cd-hk-03968%2Cj-105-ACMR-ACM%20Research%20Inc-A%2Ca-sz-300750-%u5B81%u5FB7%u65F6%u4EE3%2Ca-sz-002409-%u96C5%u514B%u79D1%u6280%2Ca-sz-002508-%u8001%u677F%u7535%u5668%2Ca-sz-000725-%u4EAC%u4E1C%u65B9%uFF21%2Ca-sh-600519-%u8D35%u5DDE%u8305%u53F0%2Ca-sz-000858-%u4E94%20%u7CAE%20%u6DB2%2Ca-sz-002415-%u6D77%u5EB7%u5A01%u89C6%2Ca-sz-002812-%u6069%u6377%u80A1%u4EFD; EMFUND0=09-11%2015%3A47%3A46@%23%24%u5BCC%u56FD%u4E2D%u8BC1%u519B%u5DE5%u6307%u6570%28LOF%29A@%23%24161024; EMFUND1=09-11%2015%3A50%3A56@%23%24%u5BCC%u56FD%u5168%u7403%u79D1%u6280%u4E92%u8054%u7F51%28QDII%29@%23%24100055; EMFUND2=09-11%2015%3A57%3A18@%23%24%u534E%u590F%u6210%u957F%u6DF7%u5408@%23%24000001; EMFUND3=09-11%2016%3A02%3A15@%23%24%u4E1C%u65B9%u963F%u5C14%u6CD5%u4F18%u52BF%u4EA7%u4E1A%u6DF7%u5408A@%23%24009644; EMFUND4=09-11%2016%3A02%3A46@%23%24%u6613%u65B9%u8FBE%u84DD%u7B79%u7CBE%u9009%u6DF7%u5408@%23%24005827; EMFUND5=09-11%2019%3A27%3A24@%23%24%u5357%u65B9%u5B9D%u5143%u503A%u5238A@%23%24202101; EMFUND6=09-11%2017%3A09%3A10@%23%24%u5357%u65B9%u4E2D%u8BC1500ETF%u8054%u63A5A@%23%24160119; EMFUND7=09-11%2017%3A04%3A25@%23%24%u56FD%u6CF0%u4E2D%u8BC1%u7164%u70ADETF@%23%24515220; EMFUND8=09-11%2019%3A26%3A02@%23%24%u56FD%u8054%u5B89%u4FE1%u5FC3%u589E%u76CA%u503A%u5238@%23%24253030; EMFUND9=09-11 22:17:55@#$%u56FD%u6CF0CES%u534A%u5BFC%u4F53%u82AF%u7247%u884C%u4E1AETF%u8054%u63A5C@%23%24008282; st_pvi=62825606404183; st_sp=2021-09-09%2020%3A52%3A54; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Fs; st_sn=48; st_psi=20210911221751816-112200305282-7125850688"
            he = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
                "Cookie": cookie,
                "Referer": "http://fundf10.eastmoney.com/",
            }
            html = requests.get(url=url, headers=he)
            html.encoding = html.apparent_encoding
            fund_data = re.findall(r'\[.*\]', html.text)[0]
            fund_data = json.loads(fund_data)
            for day_info in fund_data[::-1]:
                if not day_info["DWJZ"] or not day_info["JZZZL"]: continue
                fund_dict[day_info["FSRQ"]] = [day_info["DWJZ"], day_info["JZZZL"]]
        return fund_dict  # {时间:[净值,涨幅]}


class StrategyData(FundDb):
    def data(self):
        strategy_list = []
        db, cursor = self.db()
        sql = """select file_name from strategys;"""
        cursor.execute(sql)
        for strategy in cursor.fetchall():
            strategy_list.append(strategy["file_name"])
        db.close()
        return strategy_list


class StrategySimulate(View):  # 策略模拟
    def get(self, request):
        user = request.COOKIES.get("user")
        strategy_list_obj = StrategyData()
        strategy_list = strategy_list_obj.data()
        inform_obj = Inform()
        inform_dict = inform_obj.data()
        return render(request, "strategy_simulate.html", {
            "user": user,
            "is_post": 0,
            "strategy_list": strategy_list,
            "inform_dict": inform_dict,
        })

    def post(self, request):
        user = request.COOKIES.get("user")
        fund_id = request.POST.get("fund_id")
        date_type = request.POST.get("date")
        strategy = request.POST.get("strategy")
        strategy_list_obj = StrategyData()
        strategy_list = strategy_list_obj.data()
        fund_obj = fund_date(fund_id, date_type)
        date = fund_obj.date()
        if not date: return redirect("Error")
        strategy = getattr(importlib.import_module("fund_main_app.algorithm.{}".format(strategy)), "fund_algorithm")
        strategy_obj = strategy()
        profit_loss_list, money_list = strategy_obj.main(date, fund_id, date_type)
        # try:
        #     fund_obj = fund_date(fund_id, date_type)
        #     date = fund_obj.date()
        #     if not date: return redirect("Error")
        #     strategy = getattr(importlib.import_module("fund_main_app.algorithm.{}".format(strategy)), "fund_algorithm")
        #     strategy_obj = strategy()
        #     profit_loss_list, money_list = strategy_obj.main(date, fund_id, date_type)
        # except:
        #     return redirect("Error")
        return render(request, "strategy_simulate.html", {
            "user": user,
            "profit_loss_list": profit_loss_list,
            "money_list": money_list,
            "is_post": 1,
            "strategy_list": strategy_list
        })




class SimulateLog(View, FundDb):
    def get(self, request):
        pag = request.GET.get("pag", 0)
        pag = int(pag)
        if pag >= 1: pag = pag - 1
        user = request.COOKIES.get("user")
        sql = """select * from simulate_log order by id desc;"""
        db, cursor = self.db()
        cursor.execute(sql)
        logs = cursor.fetchall()
        for log in logs:
            if log["date_type"] == 1: log["date_type"] = "1个月"
            if log["date_type"] == 2: log["date_type"] = "6个月"
            if log["date_type"] == 3: log["date_type"] = "12个月"
        logs_obj = data.Paginator(logs, 10)
        logs = logs_obj.get_page(pag)
        sum_page = logs_obj.get_sum_page()
        sum_num = logs_obj.get_sum_num()
        inform_obj = Inform()
        inform_dict = inform_obj.data()
        return render(request, "simulate_log.html", {
            "user": user,
            "table_name": "simulate_log",
            "logs": logs,
            "sum_page": sum_page,
            "last_page": pag if pag > 1 else 1,
            "next_page": pag + 2 if pag + 2 < 10 else 10,
            "sum_num": sum_num,
            "start_page": pag * 10,
            "end_page": len(logs) + pag * 10 - 1,
            "inform_dict": inform_dict,
        })
