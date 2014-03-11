
# oscilloscope -- A digital oscilloscope, dramatize the data flow real time

## Introduction

The [Tuna](http://git.kernel.org/?p=utils/tuna/tuna.git;a=summary) project adds
a tool: oscilloscope. This tool can be used to dramatize the data flow output
from a high resolution test program:
[cyclictest](https://rt.wiki.kernel.org/index.php/Cyclictest).

I found this oscilloscope tool is very useful, it can also be used in other
scenes, so:

- To simplify its installation, I merged its original oscilloscope-cmd.py and
  tuna/oscilloscope.py.

- Add some new features, for example to monitor the background tasks
  of the Android system with adb command.

- Fix up some bugs

See more details in oscope/oscilloscope.change.log.txt.

## Use it

To draw the data, it requires the python-matplotlib package:

```
$ sudo apt-get install python-matplotlib
```

### Monitor system latency with cyclictest

Install the tool from rt-tests:

```
$ sudo apt-get install rt-tests
```

Measure system latency with verbose output:

<pre>
$ cyclictest -p99 -v
       0:     218:       3
       0:     219:       3
       0:     220:       3
       0:     221:       3
       0:     222:       4
       0:     223:       3
       0:     224:       3
       0:     225:       3
       0:     226:       4
       0:     227:       3
       0:     228:       3
       0:     229:       3
       0:     230:       3
       0:     231:       3
       0:     232:       7
       0:     233:       4
       0:     234:       3
       0:     235:       2
       0:     236:       1
       0:     237:       3
       0:     238:       4
       0:     239:       3
       0:     240:       2
       0:     241:       2
</pre>

The 3rd line is latency data. Let's draw it with oscilloscope:

```
$ sudo cyclictest -p99 -v | oscope/oscilloscope.py
```

There are 4 important generic commands to handle the drawing data:

- Space: Pause or restore monitoring
- S: Take snapshot
- R: Reset the data
- Q: Quit the drawing

**The other two commands don't support local monitoring currently, will fix
them up.**

### Monitor free memory size

First, get the free memory size from /proc/meminfo:

```
$ cat /proc/meminfo | sed -n -s '/MemFree/s/[^0-9]*\([0-9]*\).*/\1/p'
```

Then, get the free memory size in a fixed interval(E.g. 0.1s) and output the data to a pipe:

<pre>
$ mkfifo /tmp/free_mem_size
$ while :; do cat /proc/meminfo \
	| sed -n -s '/MemFree/s/[^0-9]*\([0-9]*\).*/\1/p'; sleep 0.1; done \
	> /tmp/free_mem_size &
</pre>

Monitor it:

```
$ cat /tmp/free_mem_size | ./oscope/oscilloscope.py -f0
```

### What else it can monitor?

If you want, monitor every data flow and even draw some static data.

- To optimize the cpufreq driver, use it to monitor the cpu frequency in real time.
- To observe the system TMU driver, use it to draw the temperature flow.
- To draw a file with some static data, output the data to a fifo with a fixed
  interval and draw it.
