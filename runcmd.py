#!/usr/local/bin/python

import shutil,sys,os

src = sys.argv[1]
dst = sys.argv[2]
statusFile = sys.argv[3]

file = open(statusFile, 'w+')
file.close()
shutil.copyfile(src,dst)
os.remove(statusFile)