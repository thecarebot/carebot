source /etc/environment
cd `dirname "$0"`
source ./virtualenv/bin/activate
source ./.env
eval $@
