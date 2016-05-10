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

