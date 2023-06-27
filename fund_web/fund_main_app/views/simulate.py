import re

import requests
from django.shortcuts import render, redirect
import importlib
from django.views import View


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


class StrategySimulate(View):  # 策略模拟
    def get(self, request):
        user = request.COOKIES.get("user")
        return render(request, "strategy_simulate.html",
                      {"user": user, "is_post": 0})

    def post(self, request):
        user = request.COOKIES.get("user")
        fund_id = request.POST.get("fund_id")
        date_type = request.POST.get("date")
        strategy = request.POST.get("strategy")

        try:
            fund_obj = fund_date(fund_id, date_type)
            date = fund_obj.date()
            if not date: return redirect("Error")
            strategy = getattr(importlib.import_module("fund_main_app.algorithm.{}".format(strategy)), "fund_algorithm")
            strategy_obj = strategy()
            profit_loss_list, money_list = strategy_obj.main(date)
        except:
            return redirect("Error")
        return render(request, "strategy_simulate.html",
                      {"user": user, "profit_loss_list": profit_loss_list, "money_list": money_list, "is_post": 1})


class StrategyImport(View):
    def get(self, request):
        user = request.COOKIES.get("user")
        return render(request, "strategy_import.html", {"user": user})
