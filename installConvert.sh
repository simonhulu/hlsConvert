#!/usr/bin/env bash
DIR='.'
NAME=hlsConvert.py
cp $DIR/hlsConvert.py /usr/local/bin/$NAME 
chmod a+x /usr/local/bin/$NAME
NAME=Convert.py
cp $DIR/Convert.py /usr/local/bin/$NAME
chmod a+x /usr/local/bin/$NAME
echo 'finish'
