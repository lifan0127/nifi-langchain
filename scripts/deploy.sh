#!/bin/bash

source_dir=extensions
python_extention_dir=/opt/nifi/nifi-current/python_extensions
nar_extention_dir=/opt/nifi/nifi-current/nar_extensions

rm -rf $python_extention_dir/*
rm -rf $nar_extention_dir/*
cp -r $source_dir/nifi-langchain-module/src/main/python/* $python_extention_dir
chown nifi:nifi $python_extention_dir/*
cp -r $source_dir/nifi-langchain-helper/nifi-langchain-helper-nar/target/*.nar $nar_extention_dir
chown nifi:nifi $nar_extention_dir/*