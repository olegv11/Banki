#! /bin/bash
uwsgi --stop /tmp/decks.pid
sleep 2
uwsgi --ini decks.ini & --daemonize /tmp/deckslog.log