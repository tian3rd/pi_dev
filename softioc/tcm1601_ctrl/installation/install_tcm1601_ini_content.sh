#!/bin/bash

sys=tcm1601

content_file=${sys}_ctrl_ini_content.txt
ini_file=/opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini

if grep -Fxq "${content_file}" ${ini_file}
then
    # code if found
    echo "content of ${content_file} found in ${ini_file}"
    echo "manually remove the content, and run again"
else
    # code if not found
    echo "adding content of ${content_file}"
    echo "to the ini file: ${ini_file}"
    echo "cat ../ini/${content_file} >> ${ini_file} (COMMENTED OUT!)"
fi