#! /bin/bash
uwsgi --stop /tmp/gateway.pid
uwsgi --ini gateway.ini --daemonize /tmp/gatewaylog.log
