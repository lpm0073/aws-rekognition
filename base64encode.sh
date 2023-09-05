#!/bin/sh
#------------------------------------------------------------------------------
# written by:   mcdaniel
#               https://lawrencemcdaniel.com
#
# date:         sep-2023
#
# usage:        Generate a base64 encoded representation of a binary file
#------------------------------------------------------------------------------

if [ $# == 2 ]; then
    openssl base64 -in $1 -out $2
else
    echo "base64encode.sh"
    echo "Usage: ./base64encode.sh <infile> <outfile>"
    exit 1
fi
