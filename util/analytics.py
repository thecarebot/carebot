from __future__ import division
from datetime import datetime
import logging

import app_config
from oauth import get_credentials
from util.config import Config


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config = Config()

class GoogleAnalytics:
    def __init__(self):
        self.run_time = datetime.utcnow()

    @staticmethod
    def query_ga(params):
        api_url = 'https://www.googleapis.com/analytics/v3/data/ga'
        credentials = get_credentials()
        resp = app_config.authomatic.access(credentials, api_url, params=params)
        data = resp.data
        return data

    @staticmethod
    def median(lst):
        """
        Get the median of a list of numbers
        """
        sorted_lst = sorted(lst)
        list_len = len(lst)
        index = (list_len - 1) // 2

        if list_len % 2:
            return sorted_lst[index]
        else:
            return (sorted_lst[index] + sorted_lst[index + 1])/2.0
