from plugins.npr.help import NPRHelp
from plugins.npr.linger import NPRLingerRate
from plugins.npr.overview import NPROverview
from plugins.npr.scrolldepth import NPRScrollDepth
from plugins.npr.start_tracking import NPRStartTracking

# Set up the plugins carebot will use
PLUGINS = [
    NPRHelp(),
    NPRLingerRate(),
    NPRScrollDepth(),
    NPRStartTracking(),
    NPROverview(),
]

# http://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
# http://stackoverflow.com/questions/7263101/auto-register-a-class-when-its-defined-but-without-importing-it-anywhere
