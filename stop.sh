#!/bin/sh
pid=`ps -ef | grep dmj | awk 'NR==1{print}' | awk '{print $2}'`
kill $pid
