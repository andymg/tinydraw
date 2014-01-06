# TinyDraw -- The Tools Collection For Drawing The Data

## Introduction

Data is often organized in strings, which is not that Intuitively.

To show the data more friendly, we often need to draw the data in a graph.

Different data need different tools, this project aims to collect or develop
such tools.

## Tools developed by ourselves

- [histogram](histogram/histogram.sh) draws the one row data in SVG
  with histogram

> This tool derives from  
> [(Linux)/scripts/bootgraph.pl](http://stuff.mit.edu/afs/sipb/contrib/linux/scripts/bootgraph.pl)
> and [FlameGraph](https://github.com/brendangregg/FlameGraph).

## Tools Collected From Internet

- [gnuplot](http://www.gnuplot.info/) can convert the data to a static graph.

> Gnuplot is a portable command-line driven graphing utility for Linux, OS/2,
> MS Windows, OSX, VMS, and many other platforms. The source code is
> copyrighted but freely distributed (i.e., you don't have to pay for it). It
> was originally created to allow scientists and students to visualize
> mathematical functions and data interactively, but has grown to support many
> non-interactive uses such as web scripting. It is also used as a plotting
> engine by third-party applications like Octave. Gnuplot has been supported
> and under active development since 1986.

- [systrace](http://developer.android.com/tools/help/systrace.html) exports
  [Ftrace](http://lwn.net/Articles/365835/) output to an interactive HTML
  report with AJAX feature.

> The Systrace tool helps analyze the performance of your application by
> capturing and displaying execution times of your applications processes and
> other Android system processes. The tool combines data from the Android
> kernel such as the CPU scheduler, disk activity, and application threads to
> generate an HTML report that shows an overall picture of an Android device’s
> system processes for a given period of time.

- [FlameGraph](http://www.brendangregg.com/flamegraphs.html) is able to draw a
  large number of the function call trees and the profiling data in a single
  SVG.

> Flame graphs are a visualization of profiled software, allowing the most
> frequent code-paths to be identified quickly and accurately. They can be
> generated using my Perl programs on
> <https://github.com/brendangregg/FlameGraph>, which create interactive SVGs.

- [Gprof2Dot](https://code.google.com/p/jrfonseca/wiki/Gprof2Dot) converts the
  output from many profilers into a dot graph.

> It supports many profilers: prof, gprof, VTune Amplifier XE, linux perf,
> oprofile, Valgrind's callgrind tool, sysprof, xperf, Very Sleepy, AQtime,
> python profilers, Java's HPROF; prunes nodes and edges below a certain
> threshold; uses an heuristic to propagate time inside mutually recursive
> functions; uses color efficiently to draw attention to hot-spots; works on
> any platform where Python and graphviz is available, i.e, virtually anywhere.

- [VnstatSVG](http://www.tinylab.org/project/vnstatsvg/) converts the vnStat
  output (network traffic data) to AJAX output.

> vnStatSVG is a lightweight AJAX based web front-end for network traffic
> monitoring; To use it, its backend [vnStat](http://humdi.net/vnstat/) must be
> installed at first; It only requires a CGI-supported http server but also
> generates a graphic report with SVG output, vnStatSVG is friendly to generic
> Linux hosts, servers, embedded Linux systems and even Linux clusters.
