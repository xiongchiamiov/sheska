#!/usr/bin/env python

from subprocess import Popen, PIPE

class File(object):
	def __init__(self, filename):
		self.filename = filename
		unparsedTagLine = self.call('-xmp:TagsList')
		if unparsedTagLine=='':
			self.tags = []
		else:
			self.tags = [tag.strip() for tag in unparsedTagLine.split(':')[1].split(',')]
	
	def __str__(self):
		return "%s: %s" % (self.filename, self.tags)
	
	call = lambda self, arg: Popen(['exiftool', arg, self.filename], stdout=PIPE).communicate()[0]
	
	def write_taglist(self):
		# If you aren't using digiKam, you probably want to use the Dublin Core
		# 'Subject' attribute.  That would work here, too, but adding to TagsList
		# adds the appropriate tags in digiKam even if the file's already in the
		# library, which doesn't happen with Subject.
		
		# first, erase what previously existed in the file
		self.call('-xmp:TagsList=')
		
		# and then write out all of our current tags
		for tag in self.tags:
			self.call('-xmp:TagsList+="%s"' % tag)
