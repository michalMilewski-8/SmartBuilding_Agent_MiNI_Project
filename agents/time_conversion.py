import time
from datetime import datetime

common_time_format = '%Y %m %d %H %M'


def time_to_str(date):
    return date.strftime(common_time_format)


def str_to_time(date_str):
    return datetime.strptime(date_str, common_time_format)
