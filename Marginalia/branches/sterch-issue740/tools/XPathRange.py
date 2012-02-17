#
# xpath-range.php
# representation of range in an HTML document as specified by two XPath expressions
#
# Marginalia has been developed with funding and support from
# BC Campus, Simon Fraser University, and the Government of
# Canada, and units and individuals within those organizations.
# Many thanks to all of them.  See CREDITS.html for details.
# Copyright (C) 2005-2007 Geoffrey Glass www.geof.net
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# $Id: block-range.php 45 2007-06-22 04:11:43Z geof.glass $
#

import sys
import re

class XPathRange:
	def __init__( self, rangeStr=None ):
		if rangeStr is not None and rangeStr != '':
			self.fromString( rangeStr )
		
	def fromString( self, s ):
		try:
			x = self.start
			x = self.end
			raise "Attempt to modify XPathRange"
		except AttributeError:
			pass
			
		points = s.split( ';' )
		self.start = XPathPoint( points[ 0 ].strip() )
		self.end = XPathPoint( points[ 1 ].strip() )
		
	def __repr__( self ):
		return str( self.start ) + ';' + str( self.end )


POINT_RE = re.compile( r'^(.*)\/word\((\d+)\)\/char\((\d+)\)$' )

class XPathPoint:
	def __init__( self, xpathStr, words=None, chars=None ):
		"""
		Two ways to call:
		- XPathPoint( '/p[2]/p[7]', 15, 3 )
		- XPathPoint( '/p[2]/p[7]/word(15)/char(3)' )
		"""

		xpath = xpathStr
		if words:
			self.words = int( words )
			self.chars = int( chars )
		else:
			matches = POINT_RE.match( xpathStr )
			if matches:
				xpath = matches.group( 1 )
				self.words = int( matches.group( 2 ) )
				self.chars = int( matches.group( 3 ) )
			else:
				self.words = None
				self.chars = None
		
		if not isXPathSafe( xpath ):
			raise "Unsafe XPath " + xpath
		self.path = xpath
	
	def getPathStr( self ):
		""" Get the xpath (specifying a particular element in the HTML document) """
		return self.path;
		
	def __repr__( self ):
		if self.words is None:
			return self.path
		elif self.chars is None:
			return '%s/word(%d)' % ( self.path, self.words )
		else:
			return '%s/word(%d)/char(%d)' % ( self.path, self.words, self.chars )
	
XPATH_PART_RE = re.compile( r'^[a-zA-Z0-9_:-]+\s*(.*)$' )
XPATH_TEST_RE = re.compile( r'^\[([^\]]+)\]\s*$' )
INTEGER_RE = re.compile( r'^\d+$' )
XPATH_TEST_EQUALS_RE = re.compile( r'^@[a-zA-Z0-9_-]+\s*=\s*([\'"])[^\'"]+([\'"])$' )

def isXPathSafe( xpath ):
	"""
	Check whether an untrested XPath expression is safe.  Calls to
	document(), for example, are dangerous.  This implementation
	only accepts a tiny subset of possible XPath expressions and
	may need to be extended.
	Will accept only xpaths components like the following:
	 p[1]
	 html:p
	 following-sibling::p
	 p[@attribute='value']
	"""
	
	parts = xpath.split( '/' )
	for part in parts:
		part = part.strip( )
		matches = XPATH_PART_RE.match( part )
		if matches:
			tail = matches.group( 1 ).strip( )
			
			# Simple tag name, with or without axis and/or namespace
			if tail == '':
				pass
			# Qualification in [brackets]
			else:
				matches = XPATH_TEST_RE.match( tail )
				if matches:
					test = matches.group( 1 ).strip( )
					
					# Simple number index
					if INTEGER_RE.match( test ):
						pass
					# Comparison of an attribute with a quoted value
					else:
						matches = XPATH_TEST_EQUALS_RE.match( test )
						if matches and matches.group( 1 ) == matches.group( 2 ): # ensure quotes match
							pass
						else:
							return False
				else:
					return False
		elif part == '':
			pass
		elif part == '.':
			pass
		else:
			return False
	return True

