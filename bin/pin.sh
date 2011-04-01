#!/bin/sh

pin () {
    __pin "$@"
    __sourceit
}


__sourceit () {
    SOURCEFILE=~/.pinconf/source.sh
    if [ -f "$SOURCEFILE" ]
    then
        eval `cat $SOURCEFILE`
        rm $SOURCEFILE
    fi
}