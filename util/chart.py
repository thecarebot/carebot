from decimal import *

import logging
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
import StringIO
import requests

from util.s3 import Uploader

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3 = Uploader()

"""
Tools for managing charts
"""
class ChartTools:
    @staticmethod
    def marker_position(seconds):
        col_width = 32
        padding = 2
        width = (10 * col_width) + (9 * padding)

        if seconds > 60:
            col = 5 + (seconds / 60)
        else:
            col = seconds / 10
        col = seconds / 10

        col = col - 0.5 # Go back half a step to position in the middle

        dist_from_left = (col * col_width) + ((col - 1) * padding)

        pct = dist_from_left / width

        pct = int(round(pct * 100))
        return pct


    @staticmethod
    def add_screenshot_to_chart(screenshot_url, chart_url):
        # Fetch the two images
        chart = requests.get(chart_url)
        screenshot = requests.get(screenshot_url)

        # offset the screenshot so we have a nice buffer.
        # Let's say 10px for now.
        magic_chart_buffer = 10

        # Open them up so we can mess with them
        chart = Image.open(StringIO.StringIO(chart.content))
        screenshot = Image.open(StringIO.StringIO(screenshot.content))

        c_width, c_height = chart.size
        s_width, s_height = screenshot.size

        # Calculate the dimensions for the resized screenshot using the
        # chart's height
        h_ratio = (c_height - magic_chart_buffer * 2) / float(s_height)
        new_width = int(h_ratio * s_width)
        new_s = screenshot.resize((new_width, c_height - magic_chart_buffer * 2))

        full_width = new_width + c_width + magic_chart_buffer * 2
        full_height = c_height

        # Combine the two images
        result = Image.new('RGB', (full_width, full_height), color='#fff')
        result.paste(im=chart, box=(new_width + magic_chart_buffer, 0))
        result.paste(im=new_s, box=(magic_chart_buffer, magic_chart_buffer))

        # Get them as a buffer and save 'em to s3
        output = StringIO.StringIO()
        result.save(output, format="PNG")
        contents = output.getvalue()
        url = s3.upload(contents)
        return url
