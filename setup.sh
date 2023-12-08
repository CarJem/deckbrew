#!/bin/sh

#region Definitions
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

RED='\033[0;31m'
NC='\033[0m'
#endregion

#region Service Steps

step_prepare_services() {
    SERVICES=${1}
    USERSPACE=${2}
    
    for service in $SERVICES; do
        service_name=$(basename $service)
        service_directory=$(dirname $service)
        output_file="${service_directory}/${service_name%.*}.service"
        sed "s|\$SERVICE_DIR|${service_directory}|g" $service > $output_file
    done    
}

step_remove_services() {
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

step_restart_services() {
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

step_install_services() {
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

#endregion

#region Core Commands
install() {
    eval $(get_current_inis)
    step_prepare_services "$SYSTEM_INIs"
    step_prepare_services "$USER_INIs"

    eval $(get_current_services)
    #step_remove_services "$SYSTEM_SERVICES" "system"
    step_remove_services "$USER_SERVICES" "user"

    eval $(get_service_paths)
    #step_install_services "$SYSTEM_SERVICES_PATHS" "system"
    step_install_services "$USER_SERVICES_PATHS" "user"

    systemd_reload
}

uninstall() {
    eval $(get_current_services)

    remove_services "$SYSTEM_SERVICES" "system"
    remove_services "$USER_SERVICES" "user"
}

restart() {
    eval $(get_current_services)

    restart_services "$SYSTEM_SERVICES" "system"
    restart_services "$USER_SERVICES" "user"
}

pip_install() {
    pip install -r "$SCRIPT_DIR/user/requirements.txt"
    pip install -r "$SCRIPT_DIR/system/requirements.txt"
}

systemd_reload() {
    systemctl --user daemon-reload
    sudo systemctl daemon-reload
}
#endregion

#region Getters

get_current_services() {
    SYSTEM_SERVICES=$(systemctl list-units --type service --plain --quiet | awk '{ if (($1 ~ /^sp-gamemode-/) == 1) { print $1 }}')
    USER_SERVICES=$(systemctl --user list-units --type service --plain --quiet | awk '{ if (($1 ~ /^sp-gamemode-/) == 1) { print $1 }}')
    echo "SYSTEM_SERVICES='$SYSTEM_SERVICES'; USER_SERVICES='$USER_SERVICES'"
}

get_current_inis() {
    SYSTEM_INIs=$(find "$SCRIPT_DIR/system" -name '*.ini')
    USER_INIs=$(find "$SCRIPT_DIR/user" -name '*.ini')
    echo "SYSTEM_INIs='$SYSTEM_INIs'; USER_INIs='$USER_INIs'"
}

get_service_paths() {
    SYSTEM_SERVICES_PATHS=$(find "$SCRIPT_DIR/system" -name '*.service')
    USER_SERVICES_PATHS=$(find "$SCRIPT_DIR/user" -name '*.service')
    echo "SYSTEM_SERVICES_PATHS='$SYSTEM_SERVICES_PATHS'; USER_SERVICES_PATHS='$USER_SERVICES_PATHS'"
}

#endregion

if [ "$1" == "restart" ] || [ "$1" == "reload" ]; then
    restart
elif [ "$1" == "remove" ] || [ "$1" == "uninstall" ]; then
    uninstall
elif [ "$1" == "install"  ]; then
    install
elif [ "$1" == "pip"  ]; then
    pip_install
elif [ -n "$1" ]; then
    echo "Invalid Option: $1"
else
    install
fi








