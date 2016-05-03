from plugins.npr.help import NPRHelp
from plugins.npr.scrolldepth import NPRScrollDepth
from plugins.npr.linger import NPRLingerRate

# Set up the plugins carebot will use
PLUGINS = [
    NPRHelp(),
    NPRScrollDepth(),
    NPRLingerRate(),
]

