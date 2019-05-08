import difflib # For file diff

# For watching files (created, deleted...)
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

#Threadding for multi tasking: Watching and Scanning files
import _thread

# To copy directory
import shutil
import os

# Temp dir
import tempfile


## Global Variables ##
flag = 0
is_windows = True if os.name == 'nt' else False
if len(sys.argv) < 2:
	raise Exception("Invalid directory watch path")
	exit()
watch_dir = sys.argv[1]
backup_dir = ""

def backupFile(file):
	global is_windows
	if is_windows == True:
		shutil.copyfile(file, backup_dir+"\\")
	else:
		shutil.copyfile(file, backup_dir+"/")

def fileModification(path):
	full_path = os.path.abspath(path)
	global flag
	flag += 1
	# Watchdog detects twise modification: File and Current dir so skip second check
	if flag%2 == 0:
		return
	print(f"File modified: {full_path}")
	

	
class MyEventHandler(FileSystemEventHandler):
	def on_modified(self, event):
		_thread.start_new_thread(fileModification, (event.src_path,))
		
		
def startWatching():
	logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	# event_handler = LoggingEventHandler()
	event_handler = MyEventHandler()
	observer = Observer()
	global watch_dir
	observer.schedule(event_handler, watch_dir, recursive=True)
	observer.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
	
def startBackup():
	global is_windows, backup_dir
	
	cur_dir = os.getcwd()
	if backup_dir=="":
		backup_dir = tempfile.mkdtemp() 
	
	#print(f"Current dir: {cur_dir}")
	print(f"Backup dir: {backup_dir}")
	
	if is_windows == True:
		copytree(cur_dir, backup_dir+"\\")
	else:
		copytree(cur_dir, backup_dir+"/")
	


if __name__ == "__main__":
	startBackup()
	startWatching()