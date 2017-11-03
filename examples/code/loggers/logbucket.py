########################################################################
# Example of a minimal fixed-bucket log implementation using curses.   #
#                                                                      #
# Should be able to run on headless or X-based Linux systems.          #
########################################################################

import sys
import os
import subprocess
import curses
import time

### Sample data file
file = "./data"

### List of heading text items and list of data item column positions
headers = ["TIME","AIN0","AIN1","CH0","CH1","CH2","CH3","CH4","CH5","CH6"]
cols = [0,10,20,30,34,38,42,46,50,54]

### Length and height of presentation area in character cells
### Geometry string (window size) for xterm
###     Format: 80x25+300+300 (numbers are examples)
###         80 chars per row, 25 rows
###         upper left corner 300 pixels from left edge, 300 pixels below top
Lencols = len(cols)
Height = 20
Geometry = str(cols[-1] + 4) + "x" + str(Height + 10) + "+300+300"

### Write line to screen
def wrscr(scr, row, items, offset):
	if len(items) != Lencols:
		scr.addstr(row + offset, 0, "BAD DATA!")
	else:
		for cp in range(Lencols):
			scr.addstr(row + offset, cols[cp], items[cp])

### Read log file and build report lines
def main(stdscr):
	stdscr.clear()
	curses.curs_set(0)

	with open(file, "r") as fd:
		buckets = list()
		linecnt = 0

		for line in fd.readlines():
			line = line.strip("\n\r")
			if (linecnt > 0):
				fields = line.split(",")
				try:
					rownum = buckets.index(fields[0])
				except ValueError:
					buckets.append(fields[0])
					rownum = len(buckets) - 1
				except:
					break
				wrscr(stdscr, rownum, fields, 2)
			else:
				wrscr(stdscr, 0, headers, 0)
			linecnt += 1
			stdscr.refresh()
			time.sleep(.25)

	### Postscript and exit prompt placed 1 and 3 lines below
	### bottom of data area, which is offset 2 lines from top
	### of screen
	stdscr.addstr(Height + 2 + 1, 0, "Total lines: " + str(linecnt))
	stdscr.addstr(Height + 2 + 3, 0, "Press any key to exit ...")
	stdscr.refresh()
	stdscr.getch()

### Most X-based desktop managers for Linux/Unix have xterm, so we'll assume
### we can always create a new window using it.This is NOT true on my default
### installation of Centos 7.
### This program may run on a headless system (no X support), or under a desktop manager.
### If headless, a physically-connected display is attached to a console login session that
### accesses the entire display screen space, which we assume is big enough. If a terminal
### window under a DM is used, we spawn a new xterm sized to our requirements. ssh windows
### must be manually resized on the client host, so we treat them like physical displays.

### Operate as if it's a physical display if SSH_TTY is set (ssh login), or DISPLAY is not set
### (actual physical display). Otherwise, we use xterm to create a new window, and rerun
### this script with the '-run' option.

run = len(sys.argv) > 1 and sys.argv[1] == '-run' \
	or type(os.getenv('SSH_TTY')) != type(None) \
	or type(os.getenv('DISPLAY')) == type(None)

if run:
	curses.wrapper(main)
	sys.exit(0)
else:
	subprocess.call("xterm -font -*-fixed-medium-r-*-*-14-*-*-*-*-*-iso8859-* -geometry " + Geometry + " -e python2 " + sys.argv[0] + " -run", shell=True)

