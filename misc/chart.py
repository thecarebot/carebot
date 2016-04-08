"""
Charting playground
Used for testing image-based charts
"""

import matplotlib.pyplot as plt


font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 10,
        'color'  : '#b8b8b8' }

range = [1,2,3,4,5,6,7,8,9,10]

# Set the chart size
plt.figure(figsize=(4,2), dpi=100)

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

# Configure y-axis ticks
plt.ylim(0, 100)
ax.tick_params(axis='y', colors='#b8b8b8', labelsize=8)
plt.axes().yaxis.set_ticks_position('none')
# plt.yticks(range, ['10s', '20', '30', '40', '50', '1m', '2m'])

# Configure x-axis ticks
plt.axes().xaxis.set_ticks_position('none')
ax.tick_params(axis='x', colors='#b8b8b8', labelsize=8)
ax.xaxis.label.set_fontsize(10)
plt.xticks(range, ['10s', '20', '30', '40', '50', '1m', '2m', '3m', '4m', '5m+'])

# ax.text(1.5, 100, 'MED', fontsize=8, color='#b8b8b8')

chart = plt.bar(range, [10, 20, 30, 40, 50, 30, 25, 80, 10, 50], align="center")
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

for bar in chart:
    height = bar.get_height()
    print height
    print bar.get_x()
    if bar.get_x() == 1.6:
        print
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            1.05*height,
            "MED",
            ha='center',
            va='bottom',
            color='#b8b8b8',
            fontsize=8
        )


plt.savefig('test.png', bbox_inches='tight')
