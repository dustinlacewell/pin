#!/bin/sh

ark () {
    pyark $@
    SOURCEFILE=~/.arkconf/source.sh
    if [ -f "$SOURCEFILE" ]
    then
        eval `cat $SOURCEFILE`
        rm $SOURCEFILE
    fi
}

