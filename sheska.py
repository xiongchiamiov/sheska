#!/usr/bin/env python

from libxmp import XMPFiles, XMPMeta, object_to_dict
from libxmp.consts import XMP_NS_DC

class File(object):
	def __init__(self, filename):
		self.xmpfile = XMPFiles(file_path=filename, open_forupdate=True)
		self.xmp = self.xmpfile.get_xmp() or XMPMeta()
		self._generate_taglist()
	
	def _generate_taglist(self):
		tags = []
		dict = object_to_dict(self.xmp)
		
		if dict.has_key(XMP_NS_DC): # there may not be any Dublin Core metadata
			for entry in dict[XMP_NS_DC]:
				if entry[0].startswith('dc:subject['):
					tags.append(entry[1])
		
		self.tags = tags
	
	def write_taglist(self):
		for tag in self.tags:
			self.xmp.append_array_item(XMP_NS_DC, 'subject', tag)
	
	def close(self):
		self.xmpfile.put_xmp(self.xmp)
		self.xmpfile.close_file()
