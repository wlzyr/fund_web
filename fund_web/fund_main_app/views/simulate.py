from django.shortcuts import render, redirect
import pymysql
from django.views import View


class StrategySimulate(View):
    def get(self, request):
        user = request.COOKIES.get("user")
        return render(request, "strategy_simulate.html", {"user": user})


class StrategyImport(View):
    def get(self, request):
        user = request.COOKIES.get("user")
        return render(request, "strategy_import.html", {"user": user})
