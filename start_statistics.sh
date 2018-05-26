#! /bin/bash
uwsgi --stop /tmp/statistics.pid
sleep 2
uwsgi --ini statistics.ini & --daemonize /tmp/statisticslog.log