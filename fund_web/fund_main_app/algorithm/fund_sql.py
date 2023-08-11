# -*- coding:utf-8 -*-
import time

import pymysql
import decimal
from fund_web.settings import DB_IPADDRESS, DB_PASSWORD, PORT


class fund_sql(object):
    def __init__(self):
        self.db = pymysql.connect(host=DB_IPADDRESS, user="root", password=DB_PASSWORD, database="fund", port=PORT)
        self.cursor = self.db.cursor()
        self.sum_money = decimal.Decimal('0')
        self.sum_wave = decimal.Decimal('0')
        self.profit_loss = decimal.Decimal('0')
        self.top_money = decimal.Decimal('0')
        self.sum_money_list = []
        self.sum_wave_list = []

    def buy_r(self, buy_num, id, file_name, worth, strTime):  # 加仓数据记录
        """
        :param buy_num: 购买金额
        :param id: 基金ID
        :param file_name: 持有人
        :param worth: 净值
        :param strTime: 时间
        """
        buy_num = decimal.Decimal(str(buy_num))
        worth = decimal.Decimal(str(worth))
        self.sum_money = self.sum_money + buy_num
        self.top_money = self.sum_money if self.top_money < self.sum_money else self.top_money
        hold = buy_num / worth
        sql_week = """INSERT INTO week_journal_test(fund_id,cr_change,cr_date,ch_name) VALUES("{}","{}","{}","{}");""".format(
            id, hold, strTime, file_name)
        self.cursor.execute(sql_week)
        self.db.commit()
        sql_sum = """INSERT INTO sum_journal_test(fund_id,cr_change,cr_date,ch_name,profit_loss) VALUES("{}","{}","{}","{}","{}");""".format(
            id, hold, strTime, file_name, self.profit_loss)
        self.cursor.execute(sql_sum)
        self.db.commit()
        self.sum_money_list.append(self.sum_money)

    def sell_data(self, id, sell_num, ch_name, strTime, worth):  # 卖出数据记录
        """
        :param id: 基金ID
        :param sell_num: 卖出份额
        :param ch_name: 持有人
        :param strTime: 时间
        :param worth: 净值
        """
        sell_num = decimal.Decimal(str(sell_num))
        worth = decimal.Decimal(str(worth))
        self.sum_money = self.sum_money - (sell_num * worth)
        sql_sum = """INSERT INTO sum_journal_test(fund_id,cr_change,cr_date,ch_name,profit_loss) VALUES("{}","{}","{}","{}","{}");""".format(
            id, sell_num * -1, strTime, ch_name, self.profit_loss)
        self.cursor.execute(sql_sum)
        self.db.commit()
        update_sql = """UPDATE fund_inf_test SET hold=hold+{} WHERE fund_id='{}'AND ch_name='{}';""".format(
            sell_num * -1,
            id, ch_name)
        self.cursor.execute(update_sql)
        self.db.commit()
        self.sum_money_list.append(self.sum_money)

    def av_mount(self, date):  # >=7天的数据处理
        """
        :param date: 时间
        """
        select_sql = """select * from week_journal_test where DATE_SUB("{}", INTERVAL 7 DAY) >= date(cr_date);""".format(
            date)
        self.cursor.execute(select_sql)
        data = self.cursor.fetchall()
        for ii in data:
            update_sql = """UPDATE fund_inf_test SET hold=hold+{} WHERE fund_id='{}'AND ch_name='{}';""".format(ii[2],
                                                                                                                ii[1],
                                                                                                                ii[4])
            self.cursor.execute(update_sql)
            self.db.commit()
            delete_sql = """DELETE FROM week_journal_test WHERE id={};""".format(ii[0])
            self.cursor.execute(delete_sql)
            self.db.commit()
        self.db.commit()

    def hold(self, id):  # 持仓情况
        """
        :param id: 基金ID
        :return: 持仓数量
        """
        select_sql = """SELECT hold FROM fund_inf_test where fund_id='{}';""".format(str(id))
        self.cursor.execute(select_sql)
        data = self.cursor.fetchall()[0][0]
        return data

    def profit(self, wave):  # 涨幅情况
        """
        :param wave: 涨幅
        """
        wave = decimal.Decimal(str(wave))
        self.profit_loss += wave
        self.sum_wave = round(wave * self.sum_money * decimal.Decimal("0.01") + self.sum_wave, 4)
        self.sum_wave_list.append(self.sum_wave)

    def sum_operate(self, fund_id):  # 交易次数
        """
         :param fund_id: 基金ID
         :return: 交易次数
         """
        sql = """select count(*) from sum_journal_test where fund_id='{}';""".format(str(fund_id))
        self.cursor.execute(sql)
        operate_num = self.cursor.fetchall()[0][0]
        return operate_num

    def last_stock_up(self, fund_id):  # 最后一次操作涨幅情况
        """
        :param fund_id:  基金ID
        :return: 最后一次加仓的涨幅情况
        """
        sql = """select profit_loss from sum_journal_test where fund_id="{}" and cr_change!=0 and id=(select max(id) from sum_journal_test where fund_id="{}" and cr_change!=0 );""".format(
            fund_id, fund_id)
        self.cursor.execute(sql)
        last_profit_loss = decimal.Decimal(str(self.cursor.fetchall()[0][0]))
        return last_profit_loss

    def now_profit_loss(self):
        """
        :return: 最后最新涨幅情况
        """
        return self.profit_loss

    def date_json(self, date_list):
        """
        :param date_list:  交易日期
        :return: [[时间戳，数值]]
        """
        profit_loss_list = []  # 盈亏
        money_list = []  # 使用金额
        for date, profit_loss, money in zip(date_list, self.sum_wave_list, self.sum_money_list):
            date = int(time.mktime(time.strptime(date, "%Y-%m-%d"))) * 1000
            profit_loss_list.append([date, int(profit_loss)])
            money_list.append([date, int(money)])
        return profit_loss_list, money_list

    def simulate_log(self, fund_id, simulate_name, date_type):
        """
        :param fund_id: 基金ID
        :param simulate_name: 策略名称
        :param date_type: 时间类型 1 1个月 2 6个月 3 12个月
        """
        add_sql = """INSERT INTO simulate_log(fund_id,profit_loss,strategy,date_type,top_money) VALUES("{}","{}","{}","{}","{}");""".format(
            fund_id, self.sum_wave, simulate_name, date_type, self.top_money)
        self.cursor.execute(add_sql)
        self.db.commit()

    def clear(self):  # 数据库初始化
        update_sql = """update fund_inf_test set hold=0 where id=1;"""
        self.cursor.execute(update_sql)
        self.db.commit()
        delete_sum_sql = """delete  from sum_journal_test;"""
        self.cursor.execute(delete_sum_sql)
        self.db.commit()
        delete_week_sql = """delete  from week_journal_test;"""
        self.cursor.execute(delete_week_sql)
        self.db.commit()
        self.cursor.close()
        self.db.close()
