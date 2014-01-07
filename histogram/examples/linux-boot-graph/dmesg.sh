#!/bin/bash
#
# dmesg.sh -- Convert data of `dmesg` to two row data format
#
# Author: Wu Zhangjin <wuzhangjin@gmail.com> of TinyLab.org
# Update: Sun Jan  6 22:15:20 CST 2014


dmesg_log_file=$1

[ -z "$dmesg_log_file" ] && echo "Usage: $0 dmesg_log_file" && exit 1
[ ! -f "$dmesg_log_file" ] && echo "Usage: $0 dmesg_log_file" && exit 1

# Get the execution delta of reploader and lk
cat $dmesg_log_file \
	| tr -s ' ' \
	| cut -d' ' -f2,4- \
	| awk -F'] ' 'BEGIN{prev_ts=0;}{ if (prev_ts == 0) delta=0; else { delta=$1-prev_ts; if (prev_event != "") printf("%s %s\n", delta, prev_event); } prev_ts=$1; prev_event=$0;}' \
	| cut -d' ' -f1,3- 
