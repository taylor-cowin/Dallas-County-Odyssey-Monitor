#!/bin/bash

start-web(){

}

stop-web(){

}

start-bg(){

}

stop-bg(){

}

restart-web(){

}

restart-background-worker(){

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
}

uninstall-services(){

}



while getopts "start-web:start-bg:stop-web:stop-bg:restart-web:restart-background-worker:install-services:uninstall-services:" flag
do
    case "$flag" in
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