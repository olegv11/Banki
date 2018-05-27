#! /bin/bash
uwsgi --stop /tmp/users.pid
sleep 2
uwsgi --ini users.ini --daemonize /tmp/userslog.log
