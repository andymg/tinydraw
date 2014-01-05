
# TinyDraw -- Draw one row data in SVG with histogram

## Background

We often have some similar data listed in one row like this:

> A 5
> B 6.9
> C 3.0

The first row is data description, the second row is the data itself.

A real example may be:

5 is the execution time of program A.

To find out the programs which cost most of the execution time of the
processor, we can save the above data in data.txt and then simply sort the
result with the second row:

<pre>
$ cat data.txt | sort -k2 -g -r
B 6.9
A 5
C 3.0
</pre>

But it is still not that visuable, if we can get such graph, it may be better:

![image](pic/example.svg)

## How can we convert the data to a graph

Our histogram.sh generated it:

<pre>
$ ./histogram.sh data.txt > pic/example.svg
</pre>

Open it in moderm browsers, use chromium-browser as an example:

<pre>
$ chromium-browser pic/example.svg
</pre>

## A more meaningful example

To optimize the boot time of [Linux kernel](http://www.kernel.org), we are able
to record and measure the boot time of every kernel action with the
*initcall\_debug* and *printk.time=1* kernel parameters.

After kernel boot, we can use *dmesg* command to dump out the boot log with
timestamps:

<pre>
$ dmesg > dmesg.log
</pre>

An example is put in [dmesg.log](examples/linux-boot-graph/dmesg.log).

To draw the data, an existing script is added in
[(linux)/scripts/bootgraph.pl](http://stuff.mit.edu/afs/sipb/contrib/linux/scripts/bootgraph.pl).

It generates a SVG output, align the item length with the timestamp, but its
not that easy to find out the items cost most of the time for all of them are
put in one line, not that easy to compare all of the items.

To fix up the above issue, we simply hacked the bootgraph.pl and get a new one
as [dmesg.pl](examples/linux-boot-graph/dmesg.pl). It only output the data like
this:

<pre>
$ pushd examples/linux-boot-graph/
$ cat dmesg.log | perl dmesg.pl > boot.log
$ cat boot.log | head -5
s3c_fb_init 0.091
s5p_mipi_dsi_register 0.319
pl330_driver_init 0.019
s3c24xx_serial_modinit 4.706
PVRCore_Init 0.077
$ popd
</pre>

It looks like the one row data we introduced above, so, draw it:

<pre>
$ ./histogram.sh examples/linux-boot-graph/boot.log > examples/linux-boot-graph/boot.svg
$ chromium-browser examples/linux-boot-graph/boot.svg
</pre>
