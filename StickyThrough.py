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


import tkinter as tk;
from tkinter import ttk, colorchooser;

import itertools, json;


class StickyNote:
	def __init__(self, config: ConfigElement):
		self.config = config;
		self.window = Window();
		self.frame = self.window.frame;
		self.tools = Tools(self);
		self.tools.pack(side = tk.TOP, fill = tk.X);
		# self.note = tk.Text(self.frame, background = "yellow", border = 4, relief = tk.RAISED);
		self.note = tk.Text(self.frame, background = config["color"]);
		self.note.insert("0.0", config["text"]);
		self.note.pack(fill = tk.BOTH, expand = True);
		self.window.geometry(f"{config['width']}x{config['height']}+{config['x']}+{config['y']}");
		# self.frame.bind("<Button-1>" , lambda e: print(e));
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
			x = self.window.winfo_x() + event.x - self.offset.x;
			y = self.window.winfo_y() + event.y - self.offset.y;
			self.window.geometry(f"+{x}+{y}");
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
		pass
	pass
pass
class Tools(ttk.Frame):
	def __init__(self, note: StickyNote):
		ttk.Frame.__init__(self, note.frame);
		self.note = note;
		
		self.move_button = ttk.Label(self, text = "Move", cursor = "fleur", border = 1, relief = tk.SOLID);
		self.move_button.pack(side = tk.LEFT);
		self.dragger = Window.Dragger(self.note.window, self.move_button);
		
		self.color_picker = ttk.Button(self, text = "Color", command = self.pickColor)
		self.color_picker.pack(side = tk.LEFT);
		
		# TODO new, hide?, delete
		# TODO save on ctrl S only!
	pass
	def pickColor(self):
		text = self.note.note;
		(color_tuple, color_str) = colorchooser.askcolor(text["background"]);
		if color_str is not None: text.config(background = color_str);
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
pass
default_config: ConfigElement = {
	"x": 1000,
	"y": 100,
	"width": 200,
	"height": 200,
	"color": "yellow",
	"text": "Hello World!\n"
};

with open(__actual_dir__ + "/config.json") as f:
	notes_config: list[ConfigElement] = json.load(f);
pass

def save():
	with open(__actual_dir__ + "/config.json") as f:
		json.dump(notes_config, f);
	pass
pass

notes = [StickyNote(config) for config in notes_config];
