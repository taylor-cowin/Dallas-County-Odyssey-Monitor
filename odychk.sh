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