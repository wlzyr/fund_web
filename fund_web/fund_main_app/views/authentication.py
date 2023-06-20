import hashlib

import pymysql
from django.shortcuts import render, redirect
from django.views import View

from fund_web.settings import DB_IPADDRESS, DB_PASSWORD


class FundDb(object):  # 数据库object
    @staticmethod
    def db():
        db = pymysql.connect(host=DB_IPADDRESS, user="root", passwd=DB_PASSWORD, database="fund",
                             cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        return db, cursor


class Login(View, FundDb):  # 登录
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
            ret = redirect("Bi")
            user_obj = hashlib.sha256()
            user_obj.update(user.encode("utf-8"))
            login_status = user_obj.hexdigest()
            ret.set_cookie("login_status", login_status, expires=60 * 60 * 24)
            request.session[login_status] = login_status
            ret.set_cookie("user", user)
            return ret
        else:
            return render(request, "login.html", {"color": "form-control-red", "err": "账号密码错误"})
