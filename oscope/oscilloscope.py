#!/usr/bin/python
#
# oscilloscope -- A digital oscilloscope, dramatize the data flow real time
#
#
# Convert it to a cyclictest unrelated digital oscilloscope.
# Wu Zhangjin <wuzhangjin@gmail.com>, 2012~2013
#
# Usage:
#	$ oscilloscope -h
# Example:
#	$ cyclictest -p99 -n -v | oscilloscope 
#
# Arnaldo Carvalho de Melo <acme@redhat.com>, 2012
#
# This is based on the oscilloscope and tuna from
# http://git.kernel.org/?p=utils/tuna/tuna.git;a=summary
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import getopt, sys, gtk, time
import gobject, gtk, os, sys, copy, re, thread
from matplotlib.backends.backend_gtkagg import \
	FigureCanvasGTKAgg as figure_canvas
import matplotlib.figure, matplotlib.ticker, numpy

class histogram_frame(gtk.Frame):
	def __init__(self, title = "Statistics", width = 780, height = 100,
		     max_value = 500, nr_entries = 10,
		     facecolor = "white"):
		gtk.Frame.__init__(self, title)

		self.fraction = int(max_value / nr_entries)
		if self.fraction == 0:
			self.fraction = max_value
			nr_entries = 1
		self.max_value = max_value
		self.nr_entries = nr_entries
		self.nr_samples = 0

		table = gtk.Table(3, self.nr_entries + 1, False)
		table.set_border_width(5)
		table.set_row_spacings(5)
		table.set_col_spacings(10)
		self.add(table)
		self.buckets = [ 0, ] * (nr_entries + 1)
		self.buckets_bar = [ None, ] * (nr_entries + 1)
		self.buckets_counter = [ None, ] * (nr_entries + 1)

		prefix = "<="
		for bucket in range(self.nr_entries + 1):
			bucket_range = (bucket + 1) * self.fraction
			if bucket_range > self.max_value:
				prefix = ">"
				bucket_range = self.max_value

			label = gtk.Label("%s %d" % (prefix, bucket_range))
			label.set_alignment(0, 1)
			table.attach(label, 0, 1, bucket, bucket + 1, 0, 0, 0, 0)

			self.buckets_bar[bucket] = gtk.ProgressBar()
			table.attach(self.buckets_bar[bucket], 1, 2, bucket, bucket + 1, 0, 0, 0, 0)

			self.buckets_counter[bucket] = gtk.Label("0")
			label.set_alignment(0, 1)
			table.attach(self.buckets_counter[bucket], 2, 3, bucket, bucket + 1, 0, 0, 0, 0)

		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(facecolor))

	def add_sample(self, sample):
		if sample > self.max_value:
			bucket = self.nr_entries
		else:
			bucket = int(sample / self.fraction)
		self.nr_samples += 1
		self.buckets[bucket] += 1

	def refresh(self):
		for bucket in range(self.nr_entries + 1):
			self.buckets_counter[bucket].set_text(str(self.buckets[bucket]))
			fraction = float(self.buckets[bucket]) / self.nr_samples
			self.buckets_bar[bucket].set_fraction(fraction)

	def reset(self):
		self.buckets = [ 0, ] * (self.nr_entries + 1)
		self.nr_samples = 0

class oscilloscope_frame(gtk.Frame):

	def __init__(self, title = "Osciloscope", width = 780, height = 360,
		     nr_samples_on_screen = 250, graph_type = '-',
		     max_value = 500, plot_color = "lightgreen",
		     bg_color = "darkgreen", facecolor = "white",
		     ylabel = "Current", picker = None):

		gtk.Frame.__init__(self, title)

		self.font = { 'fontname'   : 'Liberation Sans',
			      'color'      : 'b',
			      'fontweight' : 'bold',
			      'fontsize'   : 10 }

		self.max_value = max_value
		self.nr_samples_on_screen = nr_samples_on_screen
		self.ind = numpy.arange(nr_samples_on_screen)
		self.samples = [ 0.0 ] * nr_samples_on_screen

		figure = matplotlib.figure.Figure(figsize = (10, 4), dpi = 100,
						  facecolor = facecolor)
		ax = figure.add_subplot(111)
		self.ax = ax
		ax.set_axis_bgcolor(bg_color)

		self.on_screen_samples = ax.plot(self.ind, self.samples, graph_type,
						 color = plot_color,
						 picker = picker)

		ax.set_ylim(0, max_value)
		ax.set_ylabel(ylabel, self.font)
		ax.set_xlabel("%d samples" % nr_samples_on_screen, self.font)
		ax.set_xticks(range(0, nr_samples_on_screen + 1, 20))
		#ax.set_xticklabels(range(0, nr_samples_on_screen + 1, 20))
		ax.grid(True)

		for label in ax.get_yticklabels() + ax.get_xticklabels():
			label.set(fontsize = 8)

		self.canvas = figure_canvas(figure)  # a gtk.DrawingArea
		self.canvas.set_size_request(width, height)

		self.add(self.canvas)
		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(facecolor))
		self.nr_samples = 0

	def add_sample(self, sample):
		del self.samples[0]
		self.samples.append(sample)
		self.on_screen_samples[0].set_data(self.ind, self.samples)
		self.nr_samples += 1
		if self.nr_samples <= self.nr_samples_on_screen:
			self.ax.set_xlabel("%d samples" % self.nr_samples, self.font)

	def reset(self):
		self.samples = [ 0.0 ] * self.nr_samples_on_screen
		self.nr_samples = 0
		self.on_screen_samples[0].set_data(self.ind, self.samples)

	def refresh(self):
		self.canvas.draw()
		return

def add_table_row(table, row, label_text, label_value = "0"):
	label = gtk.Label(label_text)
	label.set_use_underline(True)
	label.set_alignment(0, 1)
	table.attach(label, 0, 1, row, row + 1, 0, 0, 0, 0)

	label = gtk.Label(label_value)
	table.attach(label, 1, 2, row, row + 1, 0, 0, 0, 0)
	return label

class system_info_frame(gtk.Frame):
	def __init__(self, title = "System", facecolor = "white"):
		gtk.Frame.__init__(self, title)

		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(facecolor))

		table = gtk.Table(3, 2, False)
		table.set_border_width(5)
		table.set_row_spacings(5)
		table.set_col_spacings(10)
		self.add(table)

		try:
			# Get the system information of the target machine
			kernel = os.popen("adb shell cat /proc/version").readline().split(" ")[2].lstrip(" ")
			arch = os.popen("adb shell cat /proc/cpuinfo").readline().split(":")[1].strip("\r\n").lstrip(" ")
			mach = os.popen("adb shell cat /proc/cpuinfo | grep Hardware").readline().split(":")[1].strip("\r\n").lstrip(" ")
			add_table_row(table, 0, "Kernel Release", kernel)
			add_table_row(table, 1, "Architecture", arch)
			add_table_row(table, 2, "Machine", mach)
		except:
			u = os.uname()
			add_table_row(table, 0, "Kernel Release", u[2])
			add_table_row(table, 1, "Architecture", u[4])
			add_table_row(table, 2, "Machine", u[1])

class oscilloscope(gtk.Window):

	def __init__(self, get_sample = None, width = 800, height = 500,
		     nr_samples_on_screen = 250,
		     graph_type = '-', title = "Osciloscope",
		     max_value = 500, plot_color = "lightgreen",
		     bg_color = "darkgreen", facecolor = "white",
		     ylabel = "Current",
		     picker = None,
		     snapshot_samples = 0,
		     geometry = None, scale = True,
		     offset = 30,
		     backend = False,
		     auto = False):

		gtk.Window.__init__(self)
		if geometry:
			self.parse_geometry(geometry)
			width, height = self.get_size()
		else:
			self.set_default_size(width, height)

		self.get_sample = get_sample
		self.max_value = max_value
		self.snapshot_samples = snapshot_samples
		self.scale = scale

		self.set_title(title)

		vbox = gtk.VBox()
		vbox.set_border_width(8)
		self.add(vbox)

		stats_frame = gtk.Frame("Statistics")
		stats_frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(facecolor))

		table = gtk.Table(3, 2, False)
		table.set_border_width(5)
		table.set_row_spacings(5)
		table.set_col_spacings(10)
		stats_frame.add(table)

		self.now_label = add_table_row(table, 0, "Now")
		self.min_label = add_table_row(table, 1, "Min")
		self.avg_label = add_table_row(table, 2, "Avg")
		self.max_label = add_table_row(table, 3, "Max")

		help_frame = gtk.Frame("Help")
		help_frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(facecolor))

		table = gtk.Table(4, 2, False)
		table.set_border_width(5)
		table.set_row_spacings(5)
		table.set_col_spacings(10)
		help_frame.add(table)

		self.space_label = add_table_row(table, 0, "Space", "Pause")
		add_table_row(table, 1, "S", "Snapshot")
		add_table_row(table, 2, "R", "Reset")
		self.backend_label = add_table_row(table, 3, "B", "Record Tasks: " + ("On" if backend else "Off"))
		self.auto_label = add_table_row(table, 4, "A", "Auto Report: " + ("On" if auto else "Off"))
		add_table_row(table, 5, "Q", "Quit")

		self.scope = oscilloscope_frame("Scope",
						int(width * 0.94),
						int(height * 0.64),
						nr_samples_on_screen,
						max_value = max_value,
						graph_type = graph_type,
						picker = picker,
						ylabel = ylabel)

		self.hist = histogram_frame("Histogram", 0, 0, nr_entries = 5,
					    max_value = max_value)

		info_frame = system_info_frame()

		vbox_help_info = gtk.VBox()
		vbox_help_info.pack_start(info_frame, False, False)
		vbox_help_info.pack_end(help_frame, False, False)
		hbox = gtk.HBox()
		hbox.pack_start(vbox_help_info, False, False)
		hbox.pack_start(stats_frame, False, False)
		hbox.pack_end(self.hist, True, True)

		vbox.pack_start(self.scope, True, True)
		vbox.pack_end(hbox, True, False)

		self.show_all()

		self.getting_samples = False
		self.refreshing_screen = False
		self.now = self.max = self.min = None
		self.avg = 0
		self.total = 0
		self.nr_samples = 0
		self.default_offset = offset
		self.offset = self.default_offset
		self.up_offset = self.offset / 5
		self.down_offset = self.offset / 2
		self.down_cnt = 0
		self.DOWN_CNT = 20

	def add_sample(self, sample):
		if not self.max or self.max < sample:
			self.max = sample

		if not self.min or self.min > sample:
			self.min = sample

		self.now = sample
		self.total += sample
		self.nr_samples += 1
		self.avg = self.total / self.nr_samples
		self.scope.add_sample(sample)
		self.hist.add_sample(sample)

	def refresh(self):
		if self.scale and self.max > self.scope.max_value:
			self.scope.max_value *= 2
			self.scope.ax.set_ylim(0, self.scope.max_value)
		self.scope.refresh()
		self.hist.refresh()
		while gtk.events_pending():
			gtk.main_iteration()

	def get_samples(self, fd, condition):
		try:
			sample = self.get_sample()
			if not self.getting_samples and self.auto_stopped:
				return self.getting_samples

			prev_now, prev_min, prev_avg, prev_max = self.now, self.min, self.avg, self.max
			self.add_sample(sample)

			if self.refreshing_screen:
				if self.freezed_samples_info is not None:
					self.freezed_samples_info = None
				if self.now != prev_now:
					self.now_label.set_text("%-6.3f" % self.now)
				if self.min != prev_min:
					self.min_label.set_text("%-6.3f" % self.min)
				if self.avg != prev_avg:
					self.avg_label.set_text("%-6.3f" % self.avg)
				if self.max != prev_max:
					self.max_label.set_text("%-6.3f" % self.max)

				self.refresh()
			else:
				if self.freezed_samples_info is None:
					self.freezed_samples_info = copy.deepcopy(self.samples_info)

			if self.auto_stop:
				self.pause()
				self.auto_stopped = True

			if self.snapshot_samples == self.scope.nr_samples:
				self.snapshot()
				gtk.main_quit()
		except:
			#print "invalid sample, check the input format"
			pass
		return self.getting_samples

	def run(self, fd):
		self.connect("key_press_event", self.key_press_event)
		self.start()
		gobject.io_add_watch(fd, gobject.IO_IN | gobject.IO_PRI,
				     self.get_samples)

	def set_space_label(self, state):
		self.space_label.set_text("Running" if state else "Pause")

	def freeze_screen(self, state = False):
		self.refreshing_screen = state
		self.set_space_label(state)
		if self.auto_stopped and state:
			self.auto_stop = False
			self.auto_stopped = False
			thread.start_new_thread(self.reset,())

	def pause(self):
		self.freeze_screen()

	def stop(self):
		self.getting_samples = False
		self.refreshing_screen = False
		self.set_space_label(False)

	def start(self):
		self.getting_samples = True
		self.refreshing_screen = True
		self.set_space_label(True)

	def snapshot(self):
		self.scope.canvas.print_figure("scope_snapshot.svg")

	def reset(self):
		#self.stop()
		self.scope.max_value = self.max_value
		self.scope.ax.set_ylim(0, self.scope.max_value)
		self.scope.reset()
		self.hist.reset()
		self.min = 0
		self.max = 0
		self.avg = 0
		self.total = 0
		self.nr_samples = 0
		self.offset = self.default_offset
		self.down_cnt = 0
		#self.start()

	def switch_auto(self, state = False):
		self.auto = state
		self.auto_label.set_text("Auto Report: " + ("On" if state else "Off"))

	def switch_backend(self, state = False):
		self.backend = state
		self.backend_label.set_text("Record Tasks: " + ("On" if state else "Off"))
		if state:
			self.stop()
			self.init_backend()
			self.start()

	def key_press_event(self, widget, event):
		if event.keyval == ord(' '):
			self.freeze_screen(not self.refreshing_screen)
		elif event.keyval in (ord('s'), ord('S')):
			self.snapshot()
		elif event.keyval in (ord('r'), ord('R')):
			thread.start_new_thread(self.reset,())
		elif event.keyval in (ord('a'), ord('A')):
			self.switch_auto(not self.auto)
		elif event.keyval in (ord('b'), ord('B')):
			self.switch_backend(not self.backend)
		elif event.keyval in (ord('q'), ord('Q')):
			gtk.main_quit()

class sample_info_window(gtk.Window):

	(COL_FUNCTION, ) = range(1)

	def __init__(self, sample, parent = None):
		gtk.Window.__init__(self)
		try:
			self.set_screen(parent.get_screen())
		except AttributeError:
			self.connect('destroy', lambda *w: gtk.main_quit())

		self.set_border_width(8)
		self.set_default_size(350, 500)
		self.set_title("Sample")

		vbox = gtk.VBox(False, 8)
		self.add(vbox)

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		vbox.pack_start(sw, True, True)

		store = gtk.ListStore(gobject.TYPE_STRING)

		for entry in sample:
			if entry[0] in [ "#", "\n" ] or entry[:4] == "vim:":
				continue
			iter = store.append()
			store.set(iter, self.COL_FUNCTION, entry.strip())

		treeview = gtk.TreeView(store)
		treeview.set_rules_hint(True)

		column = gtk.TreeViewColumn("Sample Information", gtk.CellRendererText(),
					    text = self.COL_FUNCTION)
		treeview.append_column(column)

		sw.add(treeview)
		self.show_all()

class datatoscope(oscilloscope):
	def __init__(self, max_value, snapshot_samples = 0, nr_samples_on_screen = 500,
		     delimiter = ':', field = 2, ylabel = "Current",
		     geometry = None, scale = True, sample_multiplier = 1, offset = 30, graph_type = 'y-o',
		     backend = False, auto = False):
		oscilloscope.__init__(self, self.get_sample,
				      title = "Software Digital Oscilloscope",
				      graph_type = graph_type,
				      nr_samples_on_screen = nr_samples_on_screen,
				      width = 900, max_value = max_value,
				      picker = self.scope_picker,
				      snapshot_samples = snapshot_samples,
				      ylabel = ylabel, geometry = geometry,
				      scale = scale,
				      offset = offset,
				      backend = backend,
				      auto = auto)

		self.connect("destroy", self.quit)
		self.delimiter = delimiter
		self.sample_multiplier = sample_multiplier
		self.field = field
		self.samples_info = [ None, ] * nr_samples_on_screen
		self.freezed_samples_info = None
		self.backend = backend
		self.auto = auto
		self.adb_connect = False
		self.latency_tracer = False
		self.auto_stop = False
		self.auto_stopped = False
		if self.backend:
			self.init_backend()

	def init_backend(self):
		if not self.adb_connect:
			self.adb_connect = not os.system("adb shell ls 2>&1 > /dev/null")
			tracer = None
			if self.adb_connect:
				tracer = os.popen("adb shell ls /sys/kernel/debug/tracing/trace").readline()
			if tracer and not re.search('No such file or directory', tracer):
				self.latency_tracer = True
				# Limit buffer size to 1.5M
				os.popen("adb shell 'echo 15000 > /sys/kernel/debug/tracing/buffer_size_kb'")
				# Enable workqueue event tracer
				os.popen("adb shell 'echo workqueue:workqueue_queue_work > /sys/kernel/debug/tracing/set_event'")

	def report_sample(self, x, sample = None):

		if sample is None:
			if not self.refreshing_screen:
				if self.freezed_samples_info[x]:
					sample = self.freezed_samples_info[x]
			else:
				if self.samples_info[x]:
					sample = self.samples_info[x]

		if self.backend and self.latency_tracer and sample and len(sample) >= 8:
			print sample[7]
			tp_info = sample[7].strip(' ').split(' ')
			#print tp_info
			#tp_pid = tp_info[0]
			#print tp_pid
			tp_info.reverse()
			#print tp_info
			tp_name = tp_info[0].strip('\r\n')
			#print tp_name

			if re.search('kworker|ksoftirq|kthread|migration|khelper', tp_name):
				try:
					traces = os.popen("adb shell 'cat /sys/kernel/debug/tracing/trace' | grep " + tp_name).readlines()
					for entry in traces:
						if entry[0] in [ "#", "\n", "\r" ] or entry[:4] == "vim:":
							continue
						print entry.strip("\r\n")
					sample += ['\r\n']
					sample += traces
				except:
					traces = None

		if sample:
			fw = sample_info_window(sample, self)

		return False, dict()

	def scope_picker(self, line, mouseevent):
		if mouseevent.xdata is None:
			return False, dict()

		x = int(mouseevent.xdata)
		return self.report_sample(x)


	def get_sample(self):
		fields = sys.stdin.readline().split(self.delimiter)
		try:
			sample = float(fields[self.field]) * self.sample_multiplier
		except:
			print "fields=%s, self.field=%s,self.delimiter=%s" % (fields, self.field, self.delimiter)
			return None

		if not self.getting_samples or self.auto_stop:
			return sample

		del self.samples_info[0]
		sample_info= []

		time_info = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
		sample_info.append(str(sample))
		sample_info.append(time_info)

		if self.backend and self.adb_connect and self.refreshing_screen and (sample > (self.avg + self.offset)):
			self.offset += self.up_offset
			try:
				top_info = os.popen("adb shell top -n 1 -d 0 -m 8").readlines()
				del top_info[0]
				del top_info[1]
				del top_info[5]
				sample_info += top_info

				for entry in top_info:
					if entry[0] in [ "#", "\n", "\r" ] or entry[:4] == "vim:":
						continue
					print entry.strip("\r\n")

				if self.auto:
					self.auto_stop = True
					thread.start_new_thread(self.report_thread, (sample_info,))
			except:
				top_info = None

		self.samples_info.append(sample_info)
		if sample < self.avg + self.down_offset:
			self.down_cnt += 1
			if self.down_cnt > self.DOWN_CNT:
				self.down_cnt = 0
				self.offset = self.default_offset

		return sample

	def report_thread(self, sample_info):
		self.report_sample(0, sample_info)
		thread.exit_thread()

	def run(self):
		oscilloscope.run(self, sys.stdin.fileno())

	def quit(self, x):
		gtk.main_quit()

def usage():
	print '''Usage: oscilloscope [OPTIONS]
	-h, --help			Give this help list
	-d, --delimiter=CHARACTER	CHARACTER used as a delimiter [Default: :]
	-f, --field=FIELD		FIELD to plot [Default: 2]
	-g, --geometry=GEOMETRY         X geometry specification (see "X" man page)
	-m, --max_value=MAX_VALUE	MAX_VALUE for the scale
	-M, --sample_multiplier=VALUE	VALUE to multiply each sample
	-n, --noscale			Do not scale when a sample is > MAX_SCALE
	-s, --nr_samples_on_screen=NR	Show NR samples on screen
	-S, --snapshot_samples=NR	Take NR samples, a snapshot and exit
	-u, --unit=TYPE			Unit TYPE [Default: us]
	-o, --offset=OFFSET_VALUE	OFFSET_VALUE for getting background information
	-t, --type=GRAPH_TYPE		Color-LinePoint, E.g. r-o, means red with line and circle
					http://matplotlib.org/examples/pylab_examples/line_styles.html
	-b, --backend			Enable the backend monitor: Use adb or ftrace to get background
	-a, --auto			Auto stop while get high work load
'''

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:],
					   "d:f:g:hM:m:ns:S:u:o:t:ba",
					   ("geometry=",
					    "help", "max_value=",
					    "sample_multiplier=",
					    "noscale",
					    "nr_samples_on_screen=",
					    "snapshot_samples=",
					    "unit=",
					    "offset=",
					    "type="
					    "backend",
					    "auto"))
	except getopt.GetoptError, err:
		usage()
		print str(err)
		sys.exit(2)

	max_value = 250
	sample_multiplier = 1
	snapshot_samples = 0
	delimiter = ':'
	field = 2
	ylabel = "Current"
	unitlabel = "mA"
	geometry = None
	scale = True
	nr_samples_on_screen = 250
	offset = 30
	graph_type = '-'
	backend = False
	auto = False

	for o, a in opts:
		if o in ("-d", "--delimiter"):
			delimiter = a
		elif o in ("-f", "--field"):
			field = int(a)
		elif o in ("-g", "--geometry"):
			geometry = a
		elif o in ("-h", "--help"):
			usage()
			return
		elif o in ("-m", "--max_value"):
			max_value = int(a)
		elif o in ("-M", "--sample_multiplier"):
			sample_multiplier = float(a)
		elif o in ("-n", "--noscale"):
			scale = False
		elif o in ("-s", "--nr_samples_on_screen"):
			nr_samples_on_screen = int(a)
		elif o in ("-S", "--snapshot_samples"):
			snapshot_samples = int(a)
		elif o in ("-u", "--unit"):
			unitlabel = a
		elif o in ("-o", "--offset"):
			offset = int(a)
			if offset == 0:
				offset = 1
		elif o in ("-t", "--type"):
			graph_type = a
		elif o in ("-b", "--backend"):
			backend = True
		elif o in ("-a", "--auto"):
			auto = True

	o = datatoscope(max_value, snapshot_samples,
					  nr_samples_on_screen = nr_samples_on_screen,
					  delimiter = delimiter, field = field,
					  ylabel = "%s (%s)" % (ylabel, unitlabel),
					  geometry = geometry, scale = scale,
					  sample_multiplier = sample_multiplier,
					  offset = offset,
					  graph_type = graph_type,
					  backend = backend,
					  auto = auto)
	o.run()
	gtk.main()

if __name__ == '__main__':
	main()
