#!/usr/bin/perl

# Copyright 2008, Intel Corporation
#
# This file is part of the Linux kernel
#
# This program file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program in a file named COPYING; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA
#
# Authors:
# 	Arjan van de Ven <arjan@linux.intel.com>


#
# This script turns a dmesg output into a SVG graphic that shows which
# functions take how much time. You can view SVG graphics with various
# programs, including Inkscape, The Gimp and Firefox.
#
#
# For this script to work, the kernel needs to be compiled with the
# CONFIG_PRINTK_TIME configuration option enabled, and with
# "initcall_debug" passed on the kernel command line.
#
# usage:
# 	dmesg | perl scripts/bootgraph.pl > output.svg
#

use strict;

my %start;
my %end;
my %type;
my $done = 0;
my $maxtime = 0;
my $firsttime = 99999;
my $count = 0;
my %pids;
my %pidctr;

while (<>) {
	my $line = $_;
	if ($line =~ /([0-9\.]+)\].* calling  ([a-zA-Z0-9\_\.]+)\+/) {
		my $func = $2;
		if ($done == 0) {
			$start{$func} = $1;
			$type{$func} = 0;
			if ($1 < $firsttime) {
				$firsttime = $1;
			}
		}
		if ($line =~ /\@ ([0-9]+)/) {
			$pids{$func} = $1;
		}
		$count = $count + 1;
	}

	if ($line =~ /([0-9\.]+)\].* async_waiting @ ([0-9]+)/) {
		my $pid = $2;
		my $func;
		if (!defined($pidctr{$pid})) {
			$func = "wait_" . $pid . "_1";
			$pidctr{$pid} = 1;
		} else {
			$pidctr{$pid} = $pidctr{$pid} + 1;
			$func = "wait_" . $pid . "_" . $pidctr{$pid};
		}
		if ($done == 0) {
			$start{$func} = $1;
			$type{$func} = 1;
			if ($1 < $firsttime) {
				$firsttime = $1;
			}
		}
		$pids{$func} = $pid;
		$count = $count + 1;
	}

	if ($line =~ /([0-9\.]+)\].* initcall ([a-zA-Z0-9\_\.]+)\+.*returned/) {
		if ($done == 0) {
			$end{$2} = $1;
			$maxtime = $1;
		}
	}

	if ($line =~ /([0-9\.]+)\].* async_continuing @ ([0-9]+)/) {
		my $pid = $2;
		my $func =  "wait_" . $pid . "_" . $pidctr{$pid};
		$end{$func} = $1;
		$maxtime = $1;
	}
	if ($line =~ /Write protecting the/) {
		$done = 1;
	}
	if ($line =~ /Freeing unused kernel memory/) {
		$done = 1;
	}
}

if ($count == 0) {
    print STDERR <<END;
No data found in the dmesg. Make sure that 'printk.time=1' and
'initcall_debug' are passed on the kernel command line.
Usage:
      dmesg | perl scripts/bootgraph.pl > output.svg
END
    exit 1;
}

my $mult = 1950.0 / ($maxtime - $firsttime);
my $threshold2 = ($maxtime - $firsttime) / 120.0;
my $threshold = $threshold2/10;

my @initcalls = sort { $start{$a} <=> $start{$b} } keys(%start);

foreach my $key (@initcalls) {
	my $duration = $end{$key} - $start{$key};
	if ($duration >= $threshold) {

		my ($delta);

		$delta = (int(($end{$key} - $start{$key})*1000)) / 1000;

		printf("%s %s\n", $key, $delta);
	}
}
