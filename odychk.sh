#!/bin/bash

start-web(){
    exit 1
}

stop-web(){
    exit 1
}

start-bg(){
    exit 1
}

stop-bg(){
    exit 1
}

restart-web(){
    exit 1
}

restart-background-worker(){
    exit 1
}

install-services(){
    INSTALLBG="/etc/systemd/system/odychk-bg.service"
    INSTALLWEB="/etc/systemd/system/odychk-web.service"
    BASEDIR=$(cd $(dirname $0) && pwd)
    if [ -e $INSTALLBG ]
    then
        echo "Background service already installed... Skipping..."
    else
        echo "Installing background service at $INSTALLBG"
        echo "[Unit]" > $INSTALLBG
        echo "Description=OdyChk Background Worker" > $INSTALLBG
        echo "After=multi-user.target" > $INSTALLBG
        echo "\n[Service]" > $INSTALLBG
        echo "WorkingDirectory=$BASEDIR" > $INSTALLBG
        echo "User=$USER" > $INSTALLBG
        echo "Restart=always" > $INSTALLBG
        echo "ExecStart=/usr/bin/python3 $BASEDIR/odychk_worker.py" > $INSTALLBG
        echo "\n[Install]" > $INSTALLBG
        echo "WantedBy=multi-user.target" > $INSTALLBG
    fi

    if [ -e $INSTALLWEB ]
    then
        echo "Web service already installed... Skipping..."
    else
        echo "Installing web service at $INSTALLWEB"
        echo "[Unit]" > $INSTALLWEB
        echo "Description=OdyChk Flask Web Server" > $INSTALLWEB
        echo "After=multi-user.target" > $INSTALLWEB
        echo "\n[Service]" > $INSTALLWEB
        echo "WorkingDirectory=$BASEDIR" > $INSTALLWEB
        echo "User=$USER" > $INSTALLWEB
        echo "Restart=always" > $INSTALLWEB
        echo "ExecStart=/usr/bin/python3 $BASEDIR/odychk_worker.py" > $INSTALLWEB
        echo "\n[Install]" > $INSTALLWEB
        echo "WantedBy=multi-user.target" > $INSTALLWEB

    fi
    exit 1
}

uninstall-services(){
    #PROMPT - ARE YOU SURE?
    #DELETE FILES ABOVE, IF THEY EXIST
    exit 1
}

#Ensure running with perms
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root." 1>&2
    exit 1
fi

#NEEDS FIXING https://www.tutorialspoint.com/unix_commands/getopt.htm #
#Get the flags and act accordingly.
while getopt "start-web:start-bg:stop-web:stop-bg:restart-web:restart-background-worker:install-services:uninstall-services:" FLAG
do
    case $flag in
        start-web ) start-web;;
        stop-web ) stop-web;;
        start-bg ) start-bg;;
        stop-bg ) stop-bg;;
        restart-web ) restart-web ;;
        restart-background-worker ) restart-background-worker;;
        install-services ) install-services;;
        uninstall-services ) uninstall-services;;
    esac
done
echo "OdyChk v2: Available flags: start-web:start-bg:stop-web:stop-bg:restart-web:restart-background-worker:install-services:uninstall-services"
exit 1