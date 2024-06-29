from __future__ import annotations;
from typing import *;
import inspect as ins;
import sys, os, pathlib;
__actual_file__   = pathlib.Path(ins.getabsfile(ins.currentframe())).resolve();
__actual_dir__    = os.path.dirname(__actual_file__);
if __name__ == '__main__' and not __package__:
	__actual_parent__ = os.path.dirname(__actual_dir__ );
	sys.path.insert(0, __actual_parent__);
	__package__ = os.path.split(__actual_dir__)[1];
pass

in_pyw = sys.stdin is None;
pid = os.getpid();
print(f"{pid = }");

try:
	import tkinter as tk;
	from tkinter import ttk, colorchooser, messagebox, font;
	
	import itertools, json, signal;
	
	class Startup(TypedDict):
		testing: bool;
		pid: None | int;
	pass
	startup_filename = __actual_dir__ + "/startup.json";
	with open(startup_filename) as f: startup: Startup = json.load(f);
	prev_pid = startup["pid"];
	if in_pyw:
		# dont run on startup while testing
		# and dont run multiple instances
		if startup["testing"] or prev_pid: sys.exit(0);
	else:
		# running in IDLE (probably)
		#                                    != safety check
		if prev_pid is not None and prev_pid != pid: 
			try: os.kill(prev_pid, signal.SIGTERM);
			except: pass;
		pass
	pass
	startup["pid"] = pid;
	with open(startup_filename, "w") as f: json.dump(startup, f);
	
	

	class StickyNote:
		def __init__(self, config: ConfigElement):
			self.config = config;
			self.window = Window();
			self.frame = self.window.frame;
			self.tools = Tools(self);
			self.tools.pack(side = tk.TOP, fill = tk.X);
			self.title_var = tk.StringVar(self.frame, value = config["title"]);
			self.title = ttk.Entry(self.frame, textvariable = self.title_var, font = font.Font(self.window, family="Helvetica", size=14, weight="bold"), justify = tk.CENTER);
			self.title.pack(side = tk.TOP, fill = tk.X);
			self.note = tk.Text(self.frame, background = config["color"]);
			self.note.insert("0.0", config["text"]);
			self.note.pack(fill = tk.BOTH, expand = True);
			self.window.geometry(f"{config['width']}x{config['height']}+{config['x']}+{config['y']}");
			self.title_var.trace_add("write", lambda *_: saver.defer(self.title));
			self.note.bind("<<Modified>>", self.onModified);
		pass
		def onModified(self, *_):
			self.note.edit_modified(False);
			saver.defer(self.note);
		pass
		def updateConfig(self):
			window = self.window;
			text = self.note;
			self.config.update(
				x      = window.winfo_x(),
				y      = window.winfo_y(),
				width  = window.winfo_width(),
				height = window.winfo_height(),
				color  = text["background"],
				text   = text.get("0.0", tk.END),
				title  = self.title.get(),
			);
		pass
	pass
	class Window(tk.Tk):
		def __init__(self):
			tk.Tk.__init__(self);
			self.overrideredirect(True);
			frame = ttk.Frame(self, border = 1, relief = tk.SOLID);
			frame.pack(expand = True, fil = tk.BOTH);
			frame.columnconfigure(1, weight = 1);
			frame.   rowconfigure(1, weight = 1);
			frames = {(i, j): ttk.Frame(frame, cursor = Window.resize_cursors[i, j]) for (i, j) in itertools.product(range(3), range(3))};
			for ((i, j), f) in frames.items(): f.grid(row = i, column = j, sticky = tk.NSEW);
			self.frame = frames.pop((1, 1));
			self.resizers = {(i, j): Window.Resizer(self, f, (i, j)) for ((i, j), f) in frames.items()};
			for ((i, j), f) in frames.items():
				if i != 1: f.configure(height = 4);
				if j != 1: f.configure(width  = 4);
			pass
		pass
		resize_cursors = {
			(0, 0): "size_nw_se"       , (0, 1): "sb_v_double_arrow", (0, 2): "size_ne_sw",
			(1, 0): "sb_h_double_arrow", (1, 1): "arrow"            , (1, 2): "sb_h_double_arrow",
			(2, 0): "size_ne_sw"       , (2, 1): "sb_v_double_arrow", (2, 2): "size_nw_se",
		};
		class Dragger:
			def __init__(self, window: tk.Tk, sensitive: tk.Widget):
				self.window = window;
				sensitive.bind("<Button-1>" , self.onClick);
				sensitive.bind("<B1-Motion>", self.onMove);
			pass
			def onClick(self, event: tk.Event):
				self.offset = event;
			pass
			def onMove(self, event: tk.Event):
				window = self.window;
				x = window.winfo_x() + event.x - self.offset.x;
				y = window.winfo_y() + event.y - self.offset.y;
				window.geometry(f"+{x}+{y}");
				saver.defer(window);
			pass
		pass
		class Resizer:
			def __init__(self, window: tk.Tk, sensitive: tk.Widget, ij: tuple[int, int]):
				self.window = window;
				(self.i, self.j) = ij;
				sensitive.bind("<Button-1>" , self.onClick);
				sensitive.bind("<B1-Motion>", self.onMove);
			pass
			def onClick(self, event: tk.Event):
				self.offset = event;
			pass
			def onMove(self, event: tk.Event):
				window = self.window;
				dx = event.x - self.offset.x;
				dy = event.y - self.offset.y;
				if self.j == 0:
					dwidth  = -dx;
				else:
					dwidth  = +dx;
					dx = 0;
				pass
				if self.i == 0:
					dheight = -dy;
				else:
					dheight = +dy;
					dy = 0;
				pass
				x = window.winfo_x() + dx;
				y = window.winfo_y() + dy;
				height = max(window.winfo_height() + dheight, 1);
				width  = max(window.winfo_width () + dwidth , 1);
				# print((x, y), (width, height));
				window.geometry(f"{width}x{height}+{x}+{y}");
				saver.defer(window);
			pass
		pass
	pass
	class Tools(ttk.Frame):
		def __init__(self, note: StickyNote):
			ttk.Frame.__init__(self, note.frame, cursor = "fleur");
			self.note = note;
			
			# self.move_button = ttk.Label(self, text = "Move", cursor = "fleur", border = 1, relief = tk.SOLID, padding = 2);
			# self.move_button.pack(side = tk.LEFT);
			# self.dragger = Window.Dragger(self.note.window, self.move_button);
			self.dragger = Window.Dragger(self.note.window, self);
			
			self.color_picker = ttk.Button(self, cursor = "arrow", text = "Color", width = 6, command = self.pickColor);
			self.color_picker.pack(side = tk.LEFT);
			
			self.delete_button = ttk.Button(self, cursor = "arrow", text = "Del", width = 4, command = self.delete);
			self.delete_button.pack(side = tk.RIGHT);
			self.create_button = ttk.Button(self, cursor = "arrow", text = "New", width = 4, command = self.addNew);
			self.create_button.pack(side = tk.RIGHT);
			# TODO new, hide?, delete
			# TODO save on ctrl S (no button!)
		pass
		def pickColor(self):
			text = self.note.note;
			(color_tuple, color_str) = colorchooser.askcolor(text["background"]);
			if color_str is None: return;
			text.config(background = color_str);
			saver.defer(self);
		pass
		def delete(self):
			if not messagebox.askyesno(f"Delete note <{self.note.title.get()}>", "This will permanently delete this note", icon = messagebox.WARNING): return;
			index = notes.index(self.note);
			del notes[index];
			del notes_config[index];
			self.note.window.destroy();
			saver.defer(self);
		pass
		def addNew(self):
			config = getDefaultConfig();
			notes_config.append(config);
			notes.append(StickyNote(config));
			saver.defer(self);
		pass
	pass
	# note = StickyNote();
	
	class ConfigElement(TypedDict):
		x: int;
		y: int;
		width: int;
		height: int;
		color: str; # or Any
		text: str;
		title: str;
	pass
	def getDefaultConfig() -> ConfigElement: return {
		"x": 1000,
		"y": 100,
		"width": 250,
		"height": 300,
		"color": "yellow",
		"text": "Hello World!\n",
		"title": "New Note",
	};
	
	config_filename = __actual_dir__ + "/config.json";
	if not os.path.exists(config_filename): 
		with open(config_filename, "w") as f: f.write("[]");
	pass
	with open(config_filename) as f: notes_config: list[ConfigElement] = json.load(f);
	if not notes_config: notes_config.append(getDefaultConfig());
	
	class Saver:
		defer_interval_ms = 6_000;
		def immediately(self):
			self._cancel();
			self._immediately();
		pass
		def _immediately(self):
			self._current = None;
			for note in notes: note.updateConfig();
			with open(__actual_dir__ + "/config.json", "w") as f: json.dump(notes_config, f);
			print("saved");
		pass
		def defer(self, caller: tk.Widget):
			self._cancel();
			timeout_id = caller.after(self.defer_interval_ms, self._immediately);
			self._current = (caller, timeout_id);
		pass
		def _cancel(self):
			if self._current is not None:
				(prev_caller, prev_id) = self._current;
				prev_caller.after_cancel(prev_id);
			pass
		pass
		_current: None | tuple[tk.Widget, Any] = None;
	pass
	saver = Saver();
	
	notes = [StickyNote(config) for config in notes_config];
	
	# with open(__actual_dir__ + "/debug.log", "w") as f: f.write(str(sys.stdin));
	if in_pyw:
		while True:
			for note in notes:
				window = note.window;
				window.update();
				window.update_idletasks();
			pass
		pass
	pass
except:
	import sys;
	with open(__actual_dir__ + "/err.log", "w") as f:
		sys.stderr = f;
		raise;
	pass
pass