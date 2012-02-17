
import Globals
from AccessControl import ClassSecurityInfo


class RangeInfo:
	""" A RangeInfo object contains aggregated annotation information about a range. """

	security = ClassSecurityInfo()
	
	def __init__( self, url=None, sequenceRange=None, xpathRange=None, annotations=[ ] ):
		self.url = url
		self.sequenceRange = sequenceRange
		self.xpathRange = xpathRange
		self.annotations = annotations
		
	def fromAnnotation( self, annotation ):
		self.url = annotation.getUrl( )
		self.sequenceRange = annotation.getSequenceRange( )
		self.xpathRange = annotation.getXPathRange( )
		self.annotations = [ annotation ]
		
	def addAnnotation( self, annotation ):
		self.annotations.append( annotation )
		
	security.declarePublic( 'getUsers' )
	def getUsers( self ):
		users = { }
		# I'm sure there's a more Pythonic way to do this, but I'm tired and don't know it
		for annotation in self.annotations:
			username = annotation.getUserName( )
			if not users.has_key( username ):
				users[ username ] = RangeInfoUser( username )
			if 'edit' == annotation.getAction( ):
				users[ username ].edits += 1
			else:
				users[ username ].notes += 1
		return users.values( )
		
	security.declarePublic('url')
	security.declarePublic('sequenceRange')
	security.declarePublic('xpathRange')
	security.declarePublic('annotations')
		
Globals.InitializeClass( RangeInfo )


class RangeInfoUser:
	""" Used by RangeInfo to return user information aggregated from annotations """
	
	security = ClassSecurityInfo()
	
	def __init__( self, username ):
		self.username = username
		self.notes = 0
		self.edits = 0
		
	security.declarePublic( 'username' )
	security.declarePublic( 'notes' )
	security.declarePublic( 'edits' )

Globals.InitializeClass( RangeInfoUser )

	
def mergeRangeInfos( infos ):
	""" Reduce the number of range infos as much as possible.
	Subsequent infos with the same stand and end will be collapsed to a single info. """
	infos.sort( lambda a, b: a.sequenceRange.__cmp__( b.sequenceRange ) )
	
	i = 0
	while i < len( infos ) - 2:
		info = infos[ i ]
		nextInfo = infos[ i + 1 ]
		
		# If ranges are the same, collapse the blocks
		if info.sequenceRange == nextInfo.sequenceRange:
			for annotation in nextInfo.annotations:
				info.addAnnotation( annotation )
			infos.remove( nextInfo )
		else:
			i += 1
	return infos
	
	
def calculateRangeOverlaps( ranges ):
	""" Calculate overlapping regions of highlight.  Instead of listing individual highlights,
	this provides a sequence of non-overlapping ranges - each of which represents one or
	more overlapping portions of highlighted ranges, plus a depth to say how many.
	Inspired by the GPL3 annotation implementation, but not currently used anywhere.
	UNTESTED.  PROBABLY WAY OUT OF DATE. """

	starts = annotations[:]
	ends = annotations[:]
	
	starts.sort( lambda a, b: a.start.__cmp__( b.start ) )
	ends.sort( lambda a, b: a.end.__cmp__( b.end ) )
	
	overlap = None
	overlaps = [ ]
	
	start_i = 0
	end_i = 0
	depth = 0
	
	while end_i < len( ends ):
		end = ends[ end_i ]
		endBlock = end.getBlockRange( )
		endXPath = end.getXPathRange( )
		
		comp = 0
		if start_i < len( starts ):
			start = starts[ start_i ]
			startBlock = start.getBlockRange( )
			startXPath = start.getXPathRange( )
			comp = startBlock.start.__cmp__( endBlock.end )
		else:
			comp = 1	# only ends remain
			
		if 0 == comp:
			pass	# Do nothing:  one starts, one ends - it's a wash
		else:
			blockPoint = None
			xpathPoint = None
			
			if comp < 0:
				blockPoint = startBlock.start
				if startXPath:
					xpathPoint = startXPath.start
				depth += 1
				start_i += 1
			else: # comp > 0
				blockPoint = endBlock.end
				if endXPath:
					xpathPoint = endXPath.end
				depth -= 1
				end_i += 1
				
			# Close any existing overlap
			if overlap:
				overlap.blockRange.end = blockPoint
				overlap.xpathRange.end = xpathPoint
				overlaps.append( overlap )
				overlap = None
				
			# Begin any new overlap
			if depth > 0:
				overlap = Overlap( depth )
				overlap.blockRange.start = blockPoint
				overlap.xpathRange.start = xpathPoint
	return overlaps

