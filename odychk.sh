#!/bin/bash

INSTALLBG="/etc/systemd/system/odychk-bg.service"
INSTALLWEB="/etc/systemd/system/odychk-web.service"
BASEDIR=$(cd $(dirname $0) && pwd)


start-web(){
    systemctl start odychk-web.service
    echo "Started web service."
    exit 1
}

stop-web(){
    systemctl stop odychk-web.service
    echo "Stopped web service."
    exit 1
}

start-bg(){
    systemctl start odychk-bg.service
    echo "Started background worker service."
    exit 1
}

stop-bg(){
    systemctl stop odychk-bg.service
    echo "Stopped background worker service."
    exit 1
}

restart-web(){
    systemctl restart odychk-web.service
    echo "Restarted web service."
    exit 1
}

restart-background-worker(){
    systemctl restart odychk-bg.service
    echo "Restarted background worker service."
    exit 1
}

install-services(){
#BACKGROUND WORKER INSTALLATION 
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
        echo "Finished installing background worker service."
    fi

#WEB SERVICE INSTALLATION
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
        echo "Finished installing web service."
    fi
    exit 1
}

uninstall-services(){
    echo "This will uninstall the background and worker services from /etc/systemd/system. Continue? [y/N]"
    read USERINPUT
    if [ $USERINPUT == "y" || $USERINPUT == "Y" ]
    then
        echo "Removing background worker and web services."
        if [ -e $INSTALLBG ]
        then
            echo "Removing $INSTALLBG."
            rm $INSTALLBG
        else
            echo "$INSTALLBG could not be found. Checking web service."
        fi

        if [ -e $INSTALLWEB ]
        then
            echo "Removing $INSTALLWEB."
            rm $INSTALLWEB
        else
            echo "$INSTALLWEB could not be found. Exiting."
            exit 1
        fi
    else
        echo "Cancelling. Services will not be uninstalled."  
    fi
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