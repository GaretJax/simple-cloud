#!/sbin/runscript

start() {
        ebegin "Starting auth key updater"
        start-stop-daemon --start --exec $daemon --pidfile $pidfile --background --make-pidfile --stdout=$logfile
        eend $?
}

stop() {
        ebegin "Stopping auth jey updater"
        start-stop-daemon --stop --exec $daemon --pidfile $pidfile
        eend $?
}
