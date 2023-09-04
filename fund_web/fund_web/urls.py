"""fund_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from views.authentication import Login, Exit
from views.bi import Home, Error
from views.data import FundInf, Delete, Update, SumData, WeekData
from views.fund_date_set import FundFloatSet, Config
from views.simulate import StrategySimulate, SimulateLog

urlpatterns = [
    path("", Login.as_view(), name="login"),  # 登录
    path("exit/", Exit.as_view(), name="Exit"),  # 登出

    path('index/', Home.as_view(), name="Bi"),  # 数据大屏

    path('week/data/', WeekData.as_view(), name="WeekData"),  # 周数据
    path('sum/data/', SumData.as_view(), name="SumData"),  # 总数据
    path('fund/inf/', FundInf.as_view(), name="FundInf"),  # 个人基金数据
    re_path(r'del_(\w+_\w+)/(\d+)/', Delete.as_view(), name="Delete"),  # 总/周数据的删除
    re_path(r'update_(\w+_\w+)/(\d+)/', Update.as_view(), name="Update"),  # 总/周/个人数据编辑

    path('config/', Config.as_view(), name="Config"),  # 基金概括设置
    path('fund/float/set/', FundFloatSet.as_view(), name="FundFloatSet"),  # 基金涨幅设置

    path('simulate/', StrategySimulate.as_view(), name="StrategySimulate"),  # 策略模拟
    path('simulate/log/', SimulateLog.as_view(), name="SimulateLog"),  # 策略模拟记录

    path('error/', Error.as_view(), name="Error"),  # 错误页面
]
