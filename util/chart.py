from decimal import *

import logging
import matplotlib
import matplotlib.pyplot as plt

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


    """
    Set up a link to a Google Chart to create a histogram
    Row should be in the format [seconds, count]
    """
    @staticmethod
    def scroll_histogram_link(rows, median=None):
        chdt = 'chd=t:' # Chart data
        chco = 'chco=' # Colors of each bar
        chxl = 'chxl=3:|MED|4:|%20|1:||0:|' # X-axis labels

        data = []
        for row in rows:
            data.append(str(row[3]))

        chdt += ','.join(data)

        """
        Basic scroll depth chart
        cht=bhs
        chs=250x300
        chco=4b7ef0
        chd=t:5,10,15,20,25,30,45,10,20,60
        chxt=y,x,x
        chxs=0,666666,10,1,_|1,666666,10,0,_,ffffff
        chxl=0:|100%|90%|80%|70%|60%|50%|40%|30%|20%|10%|1:|0|25|50|75|100%|2:|Percent%20of%20users
        chxp=2,50
        """

        # Uses the Google Chart API
        # Super deprecated but still running!
        # https://developers.google.com/chart/image/docs/chart_params
        base = 'http://chart.googleapis.com/chart?'
        base += '&'.join([
            chdt, # Data
            'chs=200x315', # Dimensions
            'chco=4b7ef0', # Colors
            'cht=bhs',     # Type
            'chxt=y,x,x',
            'chxs=0,666666,10,1,_|1,666666,10,0,_,ffffff',
            'chxl=0:|100%|90%|80%|70%|60%|50%|40%|30%|20%|10%|1:|0|25|50|75|100%|2:|Percent%20of%20users',
            'chxp=2,50',
            'chof=png',
            'chma=10,20,10,10',
            'chbh=26,1,1', # Width, spacing, group spacing
            'chds=a' # Auto-scale
        ])

        # Append chof=validate to the URL to debug errors
        return base


    """
    Set up a link to a Google Chart to create a histogram
    Row should be in the format [seconds, count]
    """
    @staticmethod
    def linger_histogram_link(rows, median=None):
        font = {'family' : 'normal',
                'weight' : 'normal',
                'size'   : 10,
                'color'  : '#b8b8b8' }

        range = [1,2,3,4,5,6,7,8,9,10]

        data = []
        for row in rows:
            data.append(row[1])

        # Set the chart size
        plt.figure(figsize=(4,2), dpi=100)

        # Remove the plot frame lines. They are unnecessary chartjunk.
        ax = plt.subplot(111)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        # Ensure that the axis ticks only show up on the bottom and left of the plot.
        # Ticks on the right and top of the plot are generally unnecessary chartjunk.
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        # Configure y-axis ticks
        # plt.ylim(0, 100)
        plt.axes().yaxis.set_ticks_position('none')
        ax.tick_params(axis='y', colors='#b8b8b8', labelsize=8)
        plt.axes().yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

        # Configure x-axis ticks
        plt.axes().xaxis.set_ticks_position('none')
        ax.tick_params(axis='x', colors='#b8b8b8', labelsize=8)
        plt.xticks(range, ['10s', '20', '30', '40', '50', '1m', '2m', '3m', '4m', '5m+'])

        chart = plt.bar(range, data, align="center")
        chart[0].set_color('#ffcc00')
        chart[1].set_color('#ffcc00')
        chart[2].set_color('#ffcc00')
        chart[3].set_color('#ffcc00')
        chart[4].set_color('#ffcc00')
        chart[5].set_color('#12b5a3')
        chart[6].set_color('#12b5a3')
        chart[7].set_color('#12b5a3')
        chart[8].set_color('#12b5a3')
        chart[9].set_color('#3612b5')

        # Add the median marker
        if median:
            position = (median['raw_avg_seconds'] / 10) - 1
            bar = chart[position]
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                1.05*height,
                "MED",
                ha='center',
                va='bottom',
                color='#b8b8b8',
                fontsize=8
            )

        # TODO: Save to a better temp path.
        plt.savefig('tmp.png', bbox_inches='tight')
        f = open('tmp.png', 'rb')
        url = s3.upload(f)
        return url
