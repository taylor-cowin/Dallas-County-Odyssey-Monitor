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
    if [ -e /etc/systemd/system/odychk-bg.service ]
    then
        echo "Background service already installed... Skipping..."
    else
        INSTALLBG="/etc/systemd/system/odychk-bg.service"
        echo "Installing background service at $INSTALLBG"
    fi

    if [ -e /etc/systemd/system/odychk-web.service ]
    then
        echo "Web service already installed... Skipping..."
    else
        INSTALLWEB="/etc/systemd/system/odychk-web.service"
        echo "Installing web service at $INSTALLWEB"
    fi
    exit 1
}

uninstall-services(){

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