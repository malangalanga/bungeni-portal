from SequenceRange import SequencePoint
import unittest

class TestSequencePoint ( unittest.TestCase ):

	def setUp( self ):
		self.p11 = SequencePoint( '/1/1' )
		self.p77 = SequencePoint( '/7/7' )
		self.p31 = SequencePoint( '/3/1' )
		self.p11w30 = SequencePoint( '/1/1/3.0' )
		self.p31w30 = SequencePoint( '/3/1/3.0' )
		
	def testConstruct( self ):
		self.assertTrue( self.p31.path == [ 3, 1 ] )
		self.assertTrue( self.p31.words is None )
		self.assertTrue( self.p31.chars is None )
		self.assertTrue( self.p31w30.path == [ 3, 1 ] )
		self.assertTrue( self.p31w30.words == 3 )
		self.assertTrue( self.p31w30.chars == 0 )
	
	def testCompare( self ):
		self.assertTrue( self.p11 < self.p77 )
		self.assertTrue( self.p77 > self.p11 )
		self.assertTrue( self.p31 == self.p31 )
		self.assertTrue( self.p31w30 == self.p31w30 )

	def testCompareInclusive( self ):
		block = SequencePoint( '/3' )
		point1 = SequencePoint( '/3/1.1' )
		self.assertTrue( point1.compareInclusive( block ) == 0 )
		self.assertTrue( block.compareInclusive( point1 ) == 0 )
		
if __name__ == '__main__':
    unittest.main()
