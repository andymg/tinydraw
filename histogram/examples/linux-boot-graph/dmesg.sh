#!/bin/bash
#
# dmesg.sh -- Convert data format of /proc/dmesg to one row data format
#

dmesg_log_file=$1

[ -z "$dmesg_log_file" ] && echo "Usage: $0 dmesg_log_file" && exit 1
[ ! -f "$dmesg_log_file" ] && echo "Usage: $0 dmesg_log_file" && exit 1

# Get the execution delta of reploader and lk
cat $dmesg_log_file \
	| tr -s ' ' \
	| cut -d' ' -f2,4- \
	| awk -F'] ' 'BEGIN{prev_ts=0;}{ if (prev_ts == 0) delta=0; else { delta=$1-prev_ts; if (prev_event != "") printf("%s %s\n", delta, prev_event); } prev_ts=$1; prev_event=$0;}' \
	| cut -d' ' -f1,3- 
