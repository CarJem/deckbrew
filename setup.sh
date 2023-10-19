#!/bin/sh
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

RED='\033[0;31m'
NC='\033[0m'

prepare_services() {
    SERVICES=${1}
    USERSPACE=${2}
    
    for service in $SERVICES; do
        service_name=$(basename $service)
        service_directory=$(dirname $service)
        output_file="${service_directory}/${service_name%.*}.service"
        sed "s|\$SERVICE_DIR|${service_directory}|g" $service > $output_file
    done    
}

remove_services() {
    SERVICES=${1}
    USERSPACE=${2}
    
    for service in $SERVICES; do
        service_name=$(basename $service)
        echo -e "${RED}Removing: $service_name${NC}"

        if [[ $USERSPACE == "system" ]];
        then
            sudo systemctl stop $service_name
            sudo systemctl disable $service_name
        elif [[ $USERSPACE == "user" ]];
        then
            systemctl --user stop $service_name
            systemctl --user disable $service_name
        fi    
        
    done
}

restart_services() {
    SERVICES=${1}
    USERSPACE=${2}
    
    for service in $SERVICES; do
        service_name=$(basename $service)
        echo -e "${RED}Restarting: $service_name${NC}"

        if [[ $USERSPACE == "system" ]];
        then
            sudo systemctl restart $service_name
        elif [[ $USERSPACE == "user" ]];
        then
            systemctl --user restart $service_name
        fi    
        
    done
}

install_services() {
    SERVICES=${1}
    USERSPACE=${2}
    
    for service in $SERVICES; do

        service_name=$(basename $service)

        echo -e "${RED}Enabling: $service_name${NC}"

        if [[ $USERSPACE == "system" ]];
        then
            sudo systemctl enable $service
            sudo systemctl start $service_name
        elif [[ $USERSPACE == "user" ]];
        then
            systemctl --user enable $service
            systemctl --user start $service_name
        fi    
        
    done
}

SYSTEM_INIs=$(find "$SCRIPT_DIR/system" -name '*.ini')
USER_INIs=$(find "$SCRIPT_DIR/user" -name '*.ini')

if [ "$1" == "restart-services" ]; then
    SYSTEM_SERVICES=$(systemctl list-units --type service --plain --quiet | awk '{ if (($1 ~ /^sp-gamemode-/) == 1) { print $1 }}')
    USER_SERVICES=$(systemctl --user list-units --type service --plain --quiet | awk '{ if (($1 ~ /^sp-gamemode-/) == 1) { print $1 }}')

    restart_services "$SYSTEM_SERVICES" "system"
    restart_services "$USER_SERVICES" "user"
elif [ -n "$1" ]; then
    echo "Invalid Option: $1"
else
    prepare_services "$SYSTEM_INIs"
    prepare_services "$USER_INIs"

    SYSTEM_SERVICES=$(systemctl list-units --type service --plain --quiet | awk '{ if (($1 ~ /^sp-gamemode-/) == 1) { print $1 }}')
    USER_SERVICES=$(systemctl --user list-units --type service --plain --quiet | awk '{ if (($1 ~ /^sp-gamemode-/) == 1) { print $1 }}')

    remove_services "$SYSTEM_SERVICES" "system"
    remove_services "$USER_SERVICES" "user"

    SYSTEM_SERVICES_PATHS=$(find "$SCRIPT_DIR/system" -name '*.service')
    USER_SERVICES_PATHS=$(find "$SCRIPT_DIR/user" -name '*.service')

    install_services "$SYSTEM_SERVICES_PATHS" "system"
    install_services "$USER_SERVICES_PATHS" "user"

    systemctl --user daemon-reload
    sudo systemctl daemon-reload
fi








