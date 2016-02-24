source /etc/environment
cd `dirname "$0"`
echo `pwd`
source ./virtualenv/bin/activate
echo `which python`
source ./.env
eval $@
