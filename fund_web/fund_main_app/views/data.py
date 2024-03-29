# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
import pymysql
from django.views import View
from django.http import JsonResponse
import datetime

from fund_web.settings import DB_PASSWORD, DB_IPADDRESS, PORT
from views.bi import Inform, FundDb


class Paginator(object):
    """
    分页
    """

    def __init__(self, data_list, pag):
        """
        :param data_list: 数据列表
        :param pag: 每页显示条数
        """
        self.data_list = []
        self.sum_num = len(data_list)
        s = len(data_list)
        for i in range(0, s, pag):
            self.data_list.append(data_list[i:i + pag if i + pag < s else s])

    def get_page(self, page):
        """
        获取当前页数据
        :param page: 当前页
        :return: 当前页数据
        """
        return self.data_list[page]

    def get_sum_page(self):
        """
        获取总页数
        :return: 总页数
        """
        sum_page = [i + 1 for i in range(len(self.data_list))]
        return sum_page

    def get_sum_num(self):
        """
        获取总数据条数
        :return: 总数据条数
        """
        return self.sum_num


class WeekData(View, FundDb):
    """
    周数据
    """

    def _select_data(self):
        """
        查询周数据
        :return: 周数据
        """
        db, cursor = self.db()
        sql = "select * from week_journal"
        cursor.execute(sql)
        week_journal = cursor.fetchall()
        for i in week_journal:
            i["cr_date"] = datetime.datetime.strftime(i["cr_date"], '%Y-%m-%d %H:%M:%S')
        return week_journal

    def get(self, request):
        week_journal = self._select_data()  # 查询周数据
        user = request.COOKIES.get("user")
        inform_obj = Inform()
        inform_dict = inform_obj.data()  # 消息通知
        return render(request, "data_list.html", {
            "journal": week_journal, "user": user,
            "table_name": "week_journal", "inform_dict": inform_dict,
        })


class SumData(View, FundDb):
    """
    总数据
    """

    def _select_data(self, pag=0):
        """
        查询总数据
        :param pag: 页码
        :return: deal_list(数据), sum_page(总页数), sum_num(总数据条数)
        """
        db, cursor = self.db()
        sql = "select * from sum_journal ORDER BY id DESC LIMIT 100"
        cursor.execute(sql)
        sum_journal = cursor.fetchall()
        for i in sum_journal:
            i["cr_date"] = datetime.datetime.strftime(i["cr_date"], '%Y-%m-%d %H:%M:%S')
        paginator = Paginator(sum_journal, 10)
        deal_list = paginator.get_page(pag)
        sum_page = paginator.get_sum_page()
        sum_num = paginator.get_sum_num()
        return deal_list, sum_page, sum_num

    def get(self, request):
        pag = request.GET.get("pag", 0)
        pag = int(pag)
        if pag >= 1: pag = pag - 1
        sum_journal, sum_page, sum_num = self._select_data(pag)  # 总数据
        user = request.COOKIES.get("user")
        inform_obj = Inform()
        inform_dict = inform_obj.data()  # 消息通知
        return render(request, "data_list.html", {
            "journal": sum_journal,
            "user": user,
            "table_name": "sum_journal",
            "sum_page": sum_page,
            "last_page": pag if pag > 1 else 1,
            "next_page": pag + 2 if pag + 2 < 10 else 10,
            "sum_num": sum_num,
            "start_page": pag * 10,
            "end_page": len(sum_journal) + pag * 10 - 1,
            "inform_dict": inform_dict,
        })


class Delete(View, FundDb):
    """
    总/周数据的删除
    """

    def get(self, request, delete_obj, pk):
        db, cursor = self.db()
        sql = "delete from {} where id={}".format(delete_obj, pk)
        cursor.execute(sql)
        db.commit()
        db.close()
        return JsonResponse({"status": 200})


class FundInf(View, FundDb):
    """
    个基金数据
    """

    def _inf(self):
        """
        获取所有基金数据
        :return: 所有基金数据
        """
        db, cursor = self.db()
        sql = "select * from fund_inf"
        cursor.execute(sql)
        inf_data = cursor.fetchall()
        return inf_data

    def get(self, request):
        inf_data = self._inf()  # 全部基金数据
        user = request.COOKIES.get("user")
        inform_obj = Inform()
        inform_dict = inform_obj.data()  # 消息通知
        return render(request, "fund_inf.html", {
            "inf_data": inf_data,
            "user": user,
            "inform_dict": inform_dict,
        })


class Update(View, FundDb):
    """
    总/周/个人数据编辑
    """

    def get(self, request, update_obj, pk):
        value = "hold"
        if update_obj != "fund_inf":
            value = "cr_change"
        db, cursor = self.db()
        update = request.GET.get("update")
        sql = "update {} set {}={} where id={};".format(update_obj, value, update, pk)
        cursor.execute(sql)
        db.commit()
        db.close()
        return JsonResponse({"status": 200})
