import difflib # For file diff


import sys
import time
import logging
# For watching files (created, deleted...)
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

# Words and freq
import re
import string


#### Global Variables ####
flag = 0 # File modification raises 2 event handlers, so use flag to only 1.
is_windows = True if os.name == 'nt' else False
if len(sys.argv) < 2:
	raise Exception("Invalid directory watch path")
	exit()
watch_dir = sys.argv[1]


## Backup Variables ##
backup_dir = ""

## Ransomware Hyperparameter ##
words_added = 0.5 # If this amount of words are ADDED to the file(by %), alert



def wordsAndFreq(file):
	frequency = {}
	document_text = open(file, 'r')
	text_string = document_text.read().lower()
	match_pattern = re.findall(r'\b[a-z]{3,15}\b', text_string)
	 
	for word in match_pattern:
		count = frequency.get(word,0)
		frequency[word] = count + 1
		 
	frequency_list = frequency.keys()
	 
	#for words in frequency_list:
		#print(words, frequency[words])
		
	return frequency
	
	
def backupFile(file):
	file = os.path.abspath(file)
	print(f"Backing {file} to {backup_dir}")
	global is_windows
	if is_windows == True:
		shutil.copy(file, backup_dir)
	else:
		shutil.copy(file, backup_dir)

# Called when a file is modified (The body of the detector)
def fileModification(path):
	full_path = os.path.abspath(path)
	global flag
	flag += 1
	# Watchdog detects twise modification: File and Current dir so skip second check
	if flag%2 == 0:
		return
	print(f"File modified: {full_path}")
	
	frequency = wordsAndFreq(full_path)
	words_count = 0
	for word in frequency.keys():
		words_count += frequency[word]
	
	backup_words_count = 0
	print(f"Path = {path}")
	if is_windows == True:
		backup_frequency = wordsAndFreq(backup_dir+"\\"+path)
	else:
		backup_frequency = wordsAndFreq(backup_dir+"/"+path)
	
	for word in backup_frequency.keys():
		backup_words_count += backup_frequency[word]
		
	print(f"Current words: {words_count} , But before that it was: {backup_words_count}")
	delta_words_count = words_count - backup_words_count
	print(f"Delta count = {delta_words_count}")
	
	# If removed words, do nothing, no encryption will do that
	if delta_words_count > 0:
		p = delta_words_count/words_count
		print(f"Precentage # of words added: {p}")
		if p > words_added:
			print("ALERT! RANSOMWARE DETECTED!")
			exit()
	
	backupFile(full_path)
	

	
class MyEventHandler(FileSystemEventHandler):
	def on_modified(self, event):
		# When backing up files, the new thread calls a new event handler which is not good... so, no thread
		#_thread.start_new_thread(fileModification, (event.src_path,))
		fileModification(event.src_path)
		
		
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
	
	cur_dir = watch_dir
	if backup_dir=="":
		backup_dir = tempfile.mkdtemp() 
	
	#print(f"Current dir: {cur_dir}")
	print(f"Backup dir: {backup_dir}")
	
	if is_windows == True:
		copytree(cur_dir, backup_dir+"\\")
	else:
		copytree(cur_dir, backup_dir+"/")
	
def initHyperparameters():
	pass

if __name__ == "__main__":
	startBackup()
	initHyperparameters()
	startWatching()