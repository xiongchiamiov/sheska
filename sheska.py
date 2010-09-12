#!/usr/bin/env python

import json
import sys
from hashlib import md5
from subprocess import Popen, PIPE
from urllib2 import urlopen, URLError

class File(object):
	def __init__(self, filename):
		self.filename = filename
		self.tags = []
		
		# since adding and removing tags changes the md5 hash,
		# we'll store the original hash in the metadata
		print "Checking for original hash... ",
		unparsedTagLine = self.call('-xmp:md5sum')
		if unparsedTagLine:
			# we don't assign to self.hash here, because we don't want to save
			# over the already-present hash metadata
			self._hash = unparsedTagLine.split(':')[1].strip()
		else:
			print "hashing... ",
			self.hash = md5(file(filename, 'r').read()).hexdigest()
		print "ok"
	
	def _set_hash(self, hash):
		'''
		Set the value of the hash, both in an instance variable and the file's
		metadata.
		'''
		self._hash = hash
		self.call('-xmp:md5sum=%s' % hash)
	
	hash = property(fget=lambda self: self._hash,
	                fset=_set_hash)
	
	def __str__(self):
		return "%s: %s" % (self.filename, self.tags)
	
	call = lambda self, arg: Popen(['exiftool', '-overwrite_original', arg, self.filename], stdout=PIPE).communicate()[0]
	
	def write_taglist(self):
		# If you aren't using digiKam, you probably want to use the Dublin Core
		# 'Subject' attribute.  That would work here, too, but adding to TagsList
		# adds the appropriate tags in digiKam even if the file's already in the
		# library, which doesn't happen with Subject.
		
		# first, erase what previously existed in the file
		self.call('-xmp:TagsList=')
		
		# and then write out all of our current tags
		for tag in self.tags:
			self.call('-xmp:TagsList+=%s' % tag)

if __name__ == '__main__':
	for filename in sys.argv[1:]:
		sys.stdout.flush()
		sys.stderr.flush()
		print "Processing %s" % filename
		image = File(filename)
		
		print "Fetching tags from the internets..."
		# we'll just assume that the request will eventually get through
		while True:
			try:
				# %3A is a colon (':'), encoded for urls
				unparsedJson = urlopen('http://chan.sankakucomplex.com/post/index.json?tags=md5%3A' + image.hash)
				break
			except URLError:
				print "Request timed out."
		parsedJson = json.load(unparsedJson)
		if not parsedJson:
			# hmm, let's see if we can determine the original md5sum from the filename
			if len(filename.split('.')[0]) == 32:
				print "Retrying with hash implied from filename..."
				image.hash = filename.split('.')[0]
				# and then redo this stuff
				while True:
					try:
						# %3A is a colon (':'), encoded for urls
						unparsedJson = urlopen('http://chan.sankakucomplex.com/post/index.json?tags=md5%3A' + image.hash)
						break
					except URLError:
						print "Request timed out."
				parsedJson = json.load(unparsedJson)
			
			# this will always be true if we didn't go through the if statement above
			if not parsedJson:
				print "FILE_NOT_FOUND\n"
				continue
		
		# split string on spaces
		image.tags = parsedJson[0]['tags'].split(' ')
		for index, tag in enumerate(image.tags):
			newTag = tag
			if not (tag=='=_=' or tag=='-_-'):
				newTag = newTag.replace('_', ' ')
			newTag = newTag.replace('&gt;', '>')
			newTag = newTag.replace('&lt;', '<')
			newTag = newTag.replace('&amp;', '&')
			
			if newTag != tag:
				image.tags[index] = newTag
		print "Writing new tags..."
		image.write_taglist()
		print "Done!\n"
