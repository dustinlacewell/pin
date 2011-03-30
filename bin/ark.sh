#!/bin/sh

ark () {
    __ark "$@"
    __sourceit
}

cd() {
    builtin cd "$@"
    __autoit
}

pushd() {
    builtin pushd "$@"
    __autoit
}

popd() {
    builtin popd "$@"
    __autoit
}

__autoit() {
    __arkauto `pwd`
    __sourceit
}

__sourceit () {
    SOURCEFILE=~/.arkconf/source.sh
    if [ -f "$SOURCEFILE" ]
    then
        eval `cat $SOURCEFILE`
        rm $SOURCEFILE
    fi
}