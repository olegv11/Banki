#! /bin/bash
uwsgi --stop /tmp/gateway.pid
sleep 2
uwsgi --ini gateway.ini --daemonize /tmp/gatewaylog.log
