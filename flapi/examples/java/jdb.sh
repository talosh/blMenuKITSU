#!/bin/bash -x
/usr/bin/jdb \
    -sourcepath "/Users/jamesm/filmlight/dev-jsonapi-18/build/baselight/Darwin-clang-800-64/debug/obj/flapi/java/sources:$(pwd)" \
    -classpath "/Users/jamesm/filmlight/dev-jsonapi-18/build/baselight/Darwin-clang-800-64/debug/Utilities/Resources/share/flapi/java/*:$(pwd)" \
    $*
