import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        chdt = 'chd=t:' # Chart data
        chco = 'chco=' # Colors of each bar
        chxl = 'chxl=3:|MED|4:|%20|1:||0:|' # X-axis labels

        marker_position = ChartTools.marker_position(median['raw_avg_seconds'])

        counts = []
        for row in rows:
            if row[0] == 300:
                chco += '3612b5' # color
                chxl += '5%2B' # label for 5+ minutes

            elif row[0] >= 60:
                chco += '12b5a3|' # color

                minutes = str(row[0] / 60)
                if minutes == '1':
                    chxl += '1m|'
                else:
                    chxl += minutes + '|'
            else:
                chco += 'ffcc00|' # color

                # Set legend
                if row[0] == 10:
                    chxl += '10s|'
                else:
                    chxl += str(row[0]) + '|'


            counts.append(str(row[1]))

        chdt += ','.join(counts)

        """
        Chart with median lines
        cht=bvg
        chs=250x150
        chd=t:5,10,15,20,25,30,45
        chxt=x,y,t,x
        chxs=0,ff0000,12,0,lt
            1,0000ff,10,1,lt
            2,666666,10,0,l,000000
        chxl=2:|MED|3:| ,
        chxtc=3,-160
        chxp=3,43|4,43
        """

        # Uses the Google Chart API
        # Super deprecated but still running!
        # https://developers.google.com/chart/image/docs/chart_params
        base = 'http://chart.googleapis.com/chart?'
        base += '&'.join([
            chdt, # Data
            chco, # Colors
            chxl, # X-axis Labels
            'cht=bvg',
            'chs=400x200',
            'chxt=x,x,y,t,x',
            'chxs=0,b8b8b8,10,0,_|2,N*s*,b8b8b8,10,1,_|3,666666,10,0,l,666666|4,000000,1,-1,t,000000', # Blame Google Charts.
            'chxtc=4,-180', # Median marker line
            'chof=png',
            'chbh=32,2,2', # Width, spacing, group spacing
            'chma=50,10,0,0', # Padding order: left right top bottom
            'chxp=1,50|3,%s|4,%s' % (marker_position, marker_position),
            'chds=a' # Auto-scale
        ])

        # Append chof=validate to the URL to debug errors
        # print base
        return base
