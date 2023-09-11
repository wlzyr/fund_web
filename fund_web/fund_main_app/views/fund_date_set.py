from django.shortcuts import render, redirect
import pymysql
import json
import requests
from django.views import View
import time
import fund_main_app.web_socket
from chinese_calendar import is_workday
import datetime
from views.bi import Inform, FundDb


class Config(View, FundDb):  # 基金概括设置
    def _up_config(self, m, date, rate_reserve_money):
        db, cursor = self.db()
        for fund_inf in rate_reserve_money.keys():
            sql = "update fund_inf set reserve_money={},rate={},day={} where fund_id={}".format(
                rate_reserve_money[fund_inf]["reserve_money"],
                m, rate_reserve_money[fund_inf]["day"], fund_inf)
            cursor.execute(sql)
            db.commit()
        sql = "select config from config_table"
        cursor.execute(sql)
        config = cursor.fetchall()
        config = json.loads(config[0]["config"])
        is_restart = True
        # 修订config数据处
        if config["date"] == date: is_restart = False
        config["date"] = date
        config = json.dumps(config)
        sql = "update config_table set config='{}' where id=1".format(config)
        cursor.execute(sql)
        db.commit()
        db.close()
        if is_restart: fund_main_app.web_socket.main("reboot")

    def get(self, request):
        now_money = request.COOKIES.get('now_money')
        user = request.COOKIES.get("user")
        sql = "SELECT fund_id,reserve_money,rate,day,name FROM fund_inf;"
        db, cursor = self.db()
        cursor.execute(sql)
        fund_list = cursor.fetchall()
        sql = "SELECT config FROM config_table"
        cursor.execute(sql)
        config = json.loads(cursor.fetchall()[0]["config"])
        date = config["date"][0] + ':' + config["date"][1]
        new = datetime.datetime.now().date()
        is_week_end = datetime.datetime.today().weekday()
        inform_obj = Inform()
        inform_dict = inform_obj.data()
        if not is_workday(new) or (
                time.localtime().tm_hour >= 22 or time.localtime().tm_hour <= 13) or is_week_end >= 5 or (
                time.localtime().tm_hour == 14 and time.localtime().tm_min < 50):
            return render(request, "config.html", {
                "date": date, "fund_list": fund_list,
                "user": user, "now_money": now_money,
                "inform_dict": inform_dict,
            })
        else:
            return redirect("Error")

    def post(self, request):
        m, date = request.POST.get("m"), request.POST.get("date")
        date = date.split(":")
        rate_reserve_money = {}
        id_list, _, _ = self._fund_id_list()
        for fund_id in id_list:
            money = request.POST.get("money_{}".format(fund_id))
            day = request.POST.get("day_{}".format(fund_id))
            rate_reserve_money[fund_id] = {"reserve_money": money, "day": day}

        self._up_config(m, date, rate_reserve_money)
        return redirect("Bi")


class FundFloatSet(View, FundDb):  # 基金涨幅设置

    def __init__(self):
        tt_cookie = "qgqp_b_id=7110e64f9def8a6d6521b2453aff65fa; em_hq_fls=js; HAList=a-sh-600760-%u4E2D%u822A%u6C88%u98DE%2Ca-sz-002024-%u82CF%u5B81%u6613%u8D2D%2Ca-sz-000998-%u9686%u5E73%u9AD8%u79D1; intellpositionL=1472.8px; intellpositionT=2214px; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; st_si=44692806308497; st_asi=delete; ASP.NET_SessionId=vqwpjm0zjmhdms1khwsx2sey; _qddaz=QD.x7conp.ccc1ye.kr50mpfc; EMFUND0=null; EMFUND1=07-08%2023%3A48%3A06@%23%24%u534E%u590F%u4EA7%u4E1A%u5347%u7EA7%u6DF7%u5408@%23%24005774; EMFUND2=07-08%2023%3A50%3A42@%23%24%u534E%u590F%u56FD%u4F01%u6539%u9769%u6DF7%u5408@%23%24001924; EMFUND3=07-12%2016%3A07%3A31@%23%24%u4FE1%u8FBE%u6FB3%u94F6%u65B0%u80FD%u6E90%u7CBE%u9009%u6DF7%u5408@%23%24012079; EMFUND4=07-14%2021%3A04%3A26@%23%24%u5E7F%u53D1%u4EF7%u503C%u4F18%u9009%u6DF7%u5408C@%23%24011135; EMFUND5=07-14%2015%3A28%3A21@%23%24%u8D22%u901A%u667A%u6167%u6210%u957F%u6DF7%u5408C@%23%24009063; EMFUND6=07-14%2021%3A03%3A52@%23%24%u534E%u590F%u5927%u76D8%u7CBE%u9009%u6DF7%u5408A@%23%24000011; EMFUND7=07-14%2021%3A13%3A00@%23%24%u5DE5%u94F6%u517B%u80012050%u6DF7%u5408%28FOF%29@%23%24006886; EMFUND8=07-15%2022%3A57%3A42@%23%24%u91D1%u9E70%u5185%u9700%u6210%u957F%u6DF7%u5408C@%23%24009969; EMFUND9=07-15 23:01:43@#$%u524D%u6D77%u5F00%u6E90%u6CAA%u6E2F%u6DF1%u6838%u5FC3%u8D44%u6E90%u6DF7%u5408A@%23%24003304; st_pvi=98760667666399; st_sp=2021-02-19%2012%3A00%3A58; st_inirUrl=http%3A%2F%2Fwww.zodiacn.ltd%2F; st_sn=6; st_psi=20210715230142577-112200305282-9987805961"
        self.tt_he = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
            "Cookie": tt_cookie,
            "Referer": "http: // fundf10.eastmoney.com /",
        }

    def get(self, request):
        user = request.COOKIES.get("user")
        db, cursor = self.db()
        sql = """select * from new_fund_Increase;"""
        cursor.execute(sql)
        fund_list = cursor.fetchall()
        db.close()
        inform_obj = Inform()
        inform_dict = inform_obj.data()
        for fund in fund_list:
            fund_name = requests.get(url=r'http://fundgz.1234567.com.cn/js/' + fund["fund_id"] + '.js',
                                     headers=self.tt_he)
            fund["name"] = json.loads(fund_name.text[8:-2])["name"]
        return render(request, "fund_float_set.html", {"user": user, "fund_list": fund_list,
                                                       "inform_dict": inform_dict, })

    def post(self, request):
        fund_id = request.POST.get("fund_id")
        fund = requests.get(url=r'http://fundgz.1234567.com.cn/js/' + fund_id + '.js', headers=self.tt_he)
        if fund:
            db, cursor = self.db()
            sql = """insert into new_fund_Increase(fund_id) values('{}');""".format(fund_id)
            cursor.execute(sql)
            db.commit()
            db.close()
        return redirect("FundFloatSet")
