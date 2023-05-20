#!/bin/bash

echo "Install FLAPI Examples"
echo ""
echo "Where would like to install the examples? [$HOME/flapi-examples]"
read DEST

if [ -z "$DEST" ]; then
    DEST=$HOME/flapi-examples
fi

echo "Installing examples in $DEST..."
mkdir -p `dirname $DEST`
cp -r /usr/fl/baselight-5.3.17711/share/flapi/examples $DEST
chmod -R ug+rw $DEST
