#
# SequenceRange.py
# representations for points in an HTML document and for ranges (defined by of points)
#
# Marginalia has been developed with funding and support from
# BC Campus, Simon Fraser University, and the Government of
# Canada, the UNDESA Africa i-Parliaments Action Plan, and  
# units and individuals within those organizations.  Many 
# thanks to all of them.  See CREDITS.html for details.
# Copyright (C) 2005-2007 Geoffrey Glass; the United Nations
# http://www.geof.net/code/annotation
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
# $Id$
#

import sys

class SequenceRange:
	"""
	A range in an HTML document
	Used for locating highlights
	Immutable (fromString should be treated only as a constructor)
	"""

	def __init__( self, rangeStr=None ):
		if rangeStr is not None and rangeStr != '':
			self.fromString( rangeStr )
		
	def fromString( self, s ):
		try:
			x = self.start
			x = self.end
			raise "Attempt to modify SequenceRange"
		except AttributeError:
			pass

		# Standard format, e.g. /2/3.1;/2/3.5
		# try:
		points = s.split( ';' )
		self.start = SequencePoint( points[ 0 ] )
		self.end = SequencePoint( points[ 1 ] )
		# Older formats are not supported, as there was no python implementation of Marginalia
		# that used them.
		# except ValueError:
		# raise "Bad BlockRange format (" + s + ")"
			
	def __repr__( self ):
		return str( self.start ) + ';' + str( self.end )
		
	def __cmp__( self, other ):
		r = self.start.__cmp__( other.start )
		if 0 != r:
			return r
		return self.end.__cmp__( other.end )


CMP_INCLUSIVE = 0		# a:B -> 0, A:b -> 0
CMP_TOSTART = -1		# a:B -> -1, A:b -> 1
CMP_TOEND = 1			# a:B -> 1, a:B -> -1

class SequencePoint:
	"""
	Represents a point in an annotated document
	Used for locating start and end of highlight ranges
	Immutable.
	"""
	
	def __init__( self, blockStr, words=None, chars=None ):
		"""
		Two ways to call:
		- BlockPoint( '/2/7/1', 15, 3 )
		- BlockPoint( '/2/7/1/15.3' )
		"""
#		print >>sys.stderr, "SequencePoint from ", blockStr, words, chars
		
		dot = blockStr.find( '.' )
		parts = blockStr.split( '/' )
		n = len( parts )
		
		# Transform the second call style (all one string)
		# into the correct parameters for the first
		if words is None:
			if -1 == dot:
				self.words = None
				self.chars = None
			else:
				slash = blockStr.rindex( '/' )
#				print >>sys.stderr, "Slash at %d, dot at %d in '%s' -> word( %s )" % ( slash, dot, blockStr, blockStr[ slash + 1 : dot - slash ] )
				self.words = int( blockStr[ slash + 1 : dot ] )
				self.chars = int( blockStr[ dot + 1 : ] )
				blockStr = blockStr[ 0 : slash ]
				n -= 1
		else:
			self.words = int( words )
			self.chars = int( chars )
		
		# The blockStr may be padded with zeros.  Strip them.
		self.path = [ ]
		for part in parts[ 1:n ]:
			self.path.append( int( part ) )
	
	def comparePath( self, point2 ):
		""" Compare only the path components of two points """
		len1 = len( self.path )
		len2 = len( point2.path )
		for i in range( 0, min( len1, len2 ) ):
			if self.path[ i ] < point2.path[ i ]:
				return -1
			elif self.path[ i ] > point2.path[ i ]:
				return 1
		if len1 < len2:
			return -1
		elif len1 > len2:
			return 1
		else:
			return 0
	
	def compare( self, point2, underspecified=CMP_TOSTART ):
		""" Compare two points.  If one point is more specified than the other (e.g. it has
		words specified, while the other doesn't), use the inclusive parameter.  Inclusive
		of True defaults to return True in this case, False to False. """
		r = self.comparePath( point2 )
		if r != 0:
			return r
		elif self.words is None and point2.words is None:
			return 0
		elif self.words is None:		# a:B
			return underspecified
		elif point2.words is None:		# A:b
			return -1 * underspecified
		elif self.words < point2.words:
			return -1
		elif self.words > point2.words:
			return 1
		elif self.chars is None and point2.chars is None:
			return 0
		elif self.chars is None:		# a:B
			return underspecified
		elif point2.chars is None:		# A:b
			return -1 * underspecified
		elif self.chars < point2.chars:
			return -1
		elif self.chars > point2.chars:
			return 1
		else:
			return 0
			
	def compareInclusive( self, point2 ):
		return self.compare( point2, CMP_INCLUSIVE )
		
	def __cmp__( self, point2 ):
		""" Compare location with another point. """
		
		if ((self.words is None and point2.words is not None) or 
			(self.words is not None and point2.words is None) or
			(self.chars is None and point2.words is not None) or
			(self.chars is not None and point2.words is None)):
			raise "Comparison of incomparable SequencePoints."
		else:
			return self.compare( point2 );
	
	def getPathStr( self ):
		""" Get the block path as a string of slash-separated indices """
		
		s = ''
		for component in self.path:
			s += '/%d' % ( component )
		return s
	
	def getPaddedPathStr( self ):
		"""
		Get the block path a string of slash-separated indices, each one zero-padded to 4 places
		This is the storage format used in the database to allow string comparisons to order
		paths; it should not be used externally (use getPathStr instead).
		"""
		
		s = ''
		for component in self.path:
			s += '/%04d' % ( component )
		return s
	
	def __repr__( self ):
		path = self.getPathStr( )
		if self.words is None:
			return path
		elif self.chars is None:
			return path + '/' + str( self.words ) + '.'
		else:
			return path + '/' + str( self.words ) + '.' + str( self.chars )

