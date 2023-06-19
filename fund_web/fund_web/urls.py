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
from fund_main_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.login.as_view(), name="login"),
    path('index/', views.Bi.as_view(), name="Bi"),
    path('config/', views.Config.as_view(), name="Config"),
    path('week/data/', views.WeekData.as_view(), name="WeekData"),
    path('sum/data/', views.SumData.as_view(), name="SumData"),
    path('fund/inf/', views.FundInf.as_view(), name="FundInf"),
    re_path(r'del_(\w+_\w+)/(\d+)/', views.Delete.as_view(), name="Delete"),
    re_path(r'updata_(\w+_\w+)/(\d+)/', views.Updata.as_view(), name="Updata"),
    path('error/', views.Error.as_view(), name="Error"),
    path('fund/float/set/', views.FundFloatSet.as_view(), name="fund_float_set"),
]
