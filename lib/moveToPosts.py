#!/usr/bin/env python

import os, os.path, argparse, platform
from datetime import date
from glob import glob

__all__ = [
	"getMoveInfo"
]

def getMoveInfo(file):
	INPUTS = {
		"Windows": "C:\\Users\\jmartin\\Dropbox\\secondcrack\\minorthoughts",
		"Darwin": "/Users/jmartin/Dropbox/secondcrack/minorthoughts"
	}

	root = None
	if platform.system() in INPUTS:
		root = INPUTS[platform.system()]
	if root is None:
		print ("Where am I? I don't know where to move %s for you." % args.file)
		return
	
	fullPath = os.path.abspath(file)
	fileName = os.path.basename(fullPath)
	
	today = date.today()
	yearName = today.strftime("%Y")
	monthName = today.strftime("%m")
	datePrefix = today.strftime("%Y%m%d")

	# Construct the destination folder: content/posts/YYYY/MM
	folder = os.path.join(root,"content","posts",yearName,monthName)

	# Check if the destination exists, create it if not
	try:
		os.makedirs(folder)
	except OSError:
		if not os.path.isdir(folder):
			raise

	# Create the sequence number
	sequence = len(glob(os.path.join(folder,datePrefix+"*.md"))) + 1

	# File format: YYYYMMDD-seq-name
	newFile = os.path.join( folder, "%s-%s-%s" % (datePrefix,sequence,fileName) )

	return (fullPath,newFile)

if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Move a file into the content directory with an appropriate name.")
	parser.add_argument("file")

	# Go
	args = parser.parse_args()

	(fullPath,newFile) = getMoveInfo(args.file)

	try:
		os.rename(fullPath,newFile)
	except OSError as err:
		print("Error: %s" % err.strerror)
	else:
		print("Moved %s to %s" % (fullPath,newFile))
