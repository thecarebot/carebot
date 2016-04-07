import matplotlib.pyplot as plt

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 10,
        'color'  : '#b8b8b8' }

range = [1,2,3,4,5,6,7,8,9,10]

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

# Configure y-axis ticks
plt.xlim(0, 100)
ax.tick_params(axis='x', colors='#b8b8b8', labelsize=8, labelbottom='off')
plt.axes().xaxis.set_ticks_position('none')
# plt.yticks(range, ['10s', '20', '30', '40', '50', '1m', '2m'])

# Configure x-axis ticks
plt.axes().yaxis.set_ticks_position('none')
ax.tick_params(axis='y', colors='#b8b8b8', labelsize=8)
ax.yaxis.label.set_fontsize(10)
plt.yticks(range, ['100%', '', '', '', '', '50%', '', '', '', '10%'])

chart = plt.barh(range, [10, 20, 30, 40, 50, 30, 25, 80, 10, 50], align="center")
# TODO: Set colors in one sweep
chart[0].set_color('#4b7ef0')
chart[1].set_color('#4b7ef0')
chart[2].set_color('#4b7ef0')
chart[3].set_color('#4b7ef0')
chart[4].set_color('#4b7ef0')
chart[5].set_color('#4b7ef0')
chart[6].set_color('#4b7ef0')
chart[7].set_color('#4b7ef0')
chart[8].set_color('#4b7ef0')
chart[9].set_color('#4b7ef0')


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


plt.savefig('test.png', bbox_inches='tight')
