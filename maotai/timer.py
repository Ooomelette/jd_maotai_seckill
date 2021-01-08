# -*- coding:utf-8 -*-
import time
import requests
import json

from datetime import datetime
from maotai.jd_logger import logger
from maotai.config import global_config


class Timer(object):
    def __init__(self, sleep_interval=0.2):
        # '2018-09-28 22:45:50.000'
        # buy_time = 2020-12-22 09:59:59.500
        localtime = time.localtime(time.time())
        buy_time_everyday = global_config.getRaw('config', 'buy_time').__str__()

        last_purchase_time_everyday = global_config.getRaw('config', 'last_purchase_time').__str__()

        # 开始时间
        start_time_str = localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__() + ' ' + buy_time_everyday
        self.start_time_timestramp = self.get_time_stramptimess(start_time_str)
        
        # 结束时间
        end_time_str = localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__() + ' ' + last_purchase_time_everyday
        self.end_time_timestramp = self.get_time_stramptimess(end_time_str)

        logger.info('开始时间： {}， 结束时间： {}'.format(start_time_str, end_time_str))

        self.sleep_interval = sleep_interval

        self.diff_time = self.local_jd_time_diff()


        # >>> import time
        #     >>> time.localtime(time.time())
        #     time.struct_time(tm_year=2019, tm_mon=5, tm_mday=27, tm_hour=2, tm_min=32, tm_sec=50, tm_wday=0, tm_yday=147, tm_isdst=0)
    def get_time_stramptimess(self, timestr):
        """
        timestr = '2019-01-14 15:22:18.123'
        转换成本地毫秒时间
        :return:
        """
        datetime_obj = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
        return int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0) 

    def in_skill_time(self):
        """
        本地时间减去与京东的时间差，能够将时间误差提升到0.1秒附近
        具体精度依赖获取京东服务器时间的网络时间损耗
        是否再秒杀时间内
        :return:
        """
        if self.local_time() - self.diff_time < self.start_time_timestramp:
            return False
        elif self.local_time() > self.end_time_timestramp:
            return False
        else:
            return True
        

    def jd_time(self):
        """
        从京东服务器获取时间毫秒
        :return:
        """
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)
        return int(js["serverTime"])

    def local_time(self):
        """
        获取本地毫秒时间
        :return:
        """
        return int(round(time.time() * 1000))

    def local_jd_time_diff(self):
        """
        计算本地与京东服务器时间差
        :return:
        """
        return self.local_time() - self.jd_time()

    def start(self):
        logger.info('检测本地时间与京东服务器时间误差为【{}】毫秒'.format(self.diff_time))
        while True:
            if self.in_skill_time():
                logger.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)
