#Define exceptions
class RomanError(Exception): pass
class OutOfRangeError(RomanError): pass
class NotIntegerError(RomanError): pass

#Define digit mapping
romanNumeralMap = (('M',  1000),
                   ('CM', 900),
                   ('D',  500),
                   ('CD', 400),
                   ('C',  100),
                   ('XC', 90),
                   ('L',  50),
                   ('XL', 40),
                   ('X',  10),
                   ('IX', 9),
                   ('V',  5),
                   ('IV', 4),
                   ('I',  1))

def toRoman(n):
   """convert integer to Roman numeral"""
   if not (0 < n < 5000):
      raise OutOfRangeError, "number out of range (must be 1..4999)"
   if int(n) <> n:
      raise NotIntegerError, "non-integers can not be converted"

   result = ""
   for numeral, integer in romanNumeralMap:
      while n >= integer:
         result += numeral
	 n -= integer
   return result

BASE10 = "0123456789"
BASE27 = "0abcdefghijklmnopqrstuvwxyz"

def toAlpha(number):
   """convert integer to Roman numeral"""
   todigits = BASE27
   fromdigits = BASE10
   if str(number)[0]=='-':
      number = str(number)[1:]
      neg=1
   else:
      neg=0

   # make an integer out of the number
   x=long(0)
   for digit in str(number):
      x = x*len(fromdigits) + fromdigits.index(digit)
   
   # create the result in base 'len(todigits)'
   res=""
   while x>0:
      digit = x % len(todigits)
      res = todigits[digit] + res
      x /= len(todigits)
   if neg:
      res = "-"+res

   return res

