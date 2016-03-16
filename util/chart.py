import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""
Tools for managing charts
"""
class ChartTools:
    """
    Set up a link to a Google Chart to create a histogram
    Row should be in the format [seconds, count]
    """
    @staticmethod
    def linger_histogram_link(rows):
        chdt='chd=t:' # Chart data
        chco='chco=' # Colors of each bar
        chxl='chxl=1:||0:|' # X-axis labels

        counts = []
        for row in rows:
            if row[0] == 300:
                chco += '3612b5' # color
                chxl += '5%2B' # label for 5+ minutes

            elif row[0] >= 60:
                chco +='12b5a3|' # color

                minutes = str(row[0] / 60)
                if minutes == '1':
                    chxl += '1m|'
                else:
                    chxl += minutes + '|'
            else:
                chco +='ffcc00|' # color

                # Set legend
                if row[0] == 10:
                    chxl += '10s|'
                else:
                    chxl += str(row[0]) + '|'


            counts.append(str(row[1]))

        chdt += ','.join(counts)

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
            'chxt=x,x,y',
            'chxs=0,b8b8b8,10,0,_|2,N*s*,b8b8b8,10,1,_', # Blame Google Charts.
            'chof=png',
            'chma=50,10,15,0', # Padding order: left right top bottom
            'chxp=1,50',
            'chds=a' # Auto-scale
        ])

        # Append chof=validate to the URL to debug errors
        # print(base)
        return base
