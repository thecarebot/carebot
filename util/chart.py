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

    """
    Set up a link to a Google Chart to create a histogram
    Row should be in the format [seconds, count]
    """
    @staticmethod
    def scroll_histogram_link(rows,
                              median=None,
                              labels=['100%', '90%', '80%', '70%', '60%', '50%', '40%', '30%', '20%', '10%']):
        r = range(1, len(rows) + 1)
        data = []

        # Rows are drawn "upside down" so we need to reverse them:
        rows.reverse()

        print "Chart with rows"
        print rows
        for row in rows:
            data.append(row[3])

        print "Chart with data"
        print data
        # Set the chart size
        plt.figure(figsize=(2,4), dpi=100)

        # Remove the plot frame lines. They are unnecessary chartjunk.
        ax = plt.subplot(1, 1, 1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        # Ensure that the axis ticks only show up on the bottom and left of the plot.
        # Ticks on the right and top of the plot are generally unnecessary chartjunk.
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        # Configure x-axis ticks
        plt.xlim(0, 100)
        ax.tick_params(axis='x', colors='#b8b8b8', labelsize=8, labelbottom='off')
        plt.axes().xaxis.set_ticks_position('none')

        # Configure y-axis ticks
        plt.axes().yaxis.set_ticks_position('none')
        ax.tick_params(axis='y', colors='#b8b8b8', labelsize=7)
        ax.yaxis.label.set_fontsize(10)
        plt.yticks(r, labels)

        chart = plt.barh(r, data, align="center")

        # TODO: Set colors in one sweep
        # Broken out for now in case we want to play with hihlighting segments
        for index, value in enumerate(data):
            chart[index].set_color('#4b7ef0')

        # TODO: Median line
        # for bar in chart:
        #     width = bar.get_width()
        #     print width
        #     print bar.get_y()
        #     if bar.get_y() == 1.6:
        #         print
        #         ax.text(
        #             bar.get_y() + bar.get_height()/2.,
        #             1.05 * width,
        #             "MED",
        #             ha='center',
        #             va='bottom',
        #             color='#b8b8b8',
        #             fontsize=8
        #         )

        plt.savefig('tmp.png', bbox_inches='tight')
        f = open('tmp.png', 'rb')
        url = s3.upload(f)
        return url

