#! /bin/bash
uwsgi --stop /tmp/billing.pid
sleep 2
uwsgi --ini billing.ini --daemonize /tmp/billingLog.log