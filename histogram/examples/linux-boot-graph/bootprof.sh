#!/bin/bash
#
# bootprof-convert.sh -- Convert data of /proc/bootprof to two row data format
#

bootprof_log_file=$1

[ -z "$bootprof_log_file" ] && echo "Usage: $0 bootprof_log_file" && exit 1
[ ! -f "$bootprof_log_file" ] && echo "Usage: $0 bootprof_log_file" && exit 1

# Get the execution delta of reploader and lk
cat $bootprof_log_file | egrep "preloader|lk" | tr -d ' ' | tr ':' ' '

# Get the other events' execution delta
grep -v "\-\-" $bootprof_log_file \
	| egrep -v "lk|preloader|^0" \
	| awk -F' :' 'BEGIN{prev_ts=0;}{ if (prev_ts == 0) delta=0; else { delta=$1-prev_ts; if (prev_event != "") printf("%s %s\n", delta, prev_event); } prev_ts=$1; prev_event=$0;}' \
	| tr -s ' ' | cut -d ' ' -f1,4-
