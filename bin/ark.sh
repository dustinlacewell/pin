#!/bin/sh

pin () {
    __pin "$@"
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
    __pinauto `pwd`
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