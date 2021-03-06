# -*- coding: UTF-8 -*-

# note: any time a leaf node is added to the grammar, it must be added to one
# of the strings at the bottom of this file

# note: YADPRECISEYEAR needs to be updated as the centuries go on...

date_grammar_string = u"""
	S -> MONTH | MONTHDAY | DATE | YEARSAGO | DATERANGE | MONTHDAYRANGE | MONTHDAYYEARRANGE | TIMENAME


	YEARSAGO -> YAS | YAR | KAS | KAR | MAS | MAR

	YAS -> NUM osp years sp ago | NUM osp bp
	YAR -> NUM TO NUM osp years sp ago | NUM TO NUM osp bp

	KAS -> DEC osp KA
	KAR -> DEC TO DEC osp KA

	KA -> ka | ka sp ago | thousand sp years sp ago

	MAS -> DEC osp MA
	MAR -> DEC TO DEC osp MA

	MA -> ma | ma sp ago | million sp years sp ago

	NUM -> NUME | NUMQ
	NUME -> NUMLEADGROUP NUMGROUPS
	NUMQ -> CA osp NUME | NUME q | NUME s | CA osp NUME s
	NUMLEADGROUP -> n | n n | n n n
	NUMGROUP -> NUMGROUPSEP n n n
	NUMGROUPSEP -> comma |
	NUMGROUPS -> NUMGROUPS NUMGROUP |

	DEC -> DECE | DECQ | DECQQ
	DECE -> NUME x NUME | NUME
	DECQ -> CA osp DECE | DECE q
	DECQQ -> DECE osp pm osp DECE


	DATE -> YBC | YAD | PERIODBC | PERIODAD
	
	YBC -> NUM osp BC
	YAD -> YADYEAR | YADYEARMONTH | YADYEARMONTHDAY
	YADYEAR -> NUM | NUM osp AD | AD osp NUM
	YADPRECISEYEAR -> '5' n n | '1' n n n | '2' '0' n n | '2' '1' n n | '2' '2' n n
	YADYEARMONTH -> MONTH ocommadotsp YADPRECISEYEAR | YADPRECISEYEAR ocommadotsp MONTH | YADPRECISEYEAR ocommadotsp MONTH sp AD
	YADYEARMONTHDAY -> MONTHDAY ocommadotsp YADPRECISEYEAR | YADPRECISEYEAR ocommadotsp MONTHDAY | YADPRECISEYEAR ocommadotsp MONTHDAY osp AD

	PERIODBC -> PERIOD osp BC
	PERIODAD ->  PERIOD osp AD | PERIOD

	PERIOD -> ORD odashsp century | ORD odashsp millenium
	ORD -> NUM th


	DATERANGE -> DATE TO DATE | ORD TO DATE

	TO -> osp dash osp | sp to sp


	MONTHDAY -> DAY sp MONTH | MONTH ocomma sp DAY | MONTHNUM '/' DAY
	MONTH -> jan | feb | mar | apr | may | jun | jul | aug | sep | oct | nov | dec
	MONTHNUM -> '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '1' '0' | '1' '1' | '1' '2'
	DAY -> DAYNUM | DAYNUM th
	DAYNUM -> n | '0' n | '1' n | '2' n | '3' '0' | '3' '1'


	MONTHDAYRANGE -> MONTHDAY TO MONTHDAY | MONTH TO MONTHDAY | DAY TO MONTHDAY | MONTHDAY TO DAY
	MONTHDAYRANGE -> MONTHDAY TO YADYEARMONTH | MONTH TO YADYEARMONTH
	MONTHDAYRANGE -> MONTHDAY TO YADYEARMONTHDAY | MONTH TO YADYEARMONTHDAY  | DAY TO YADYEARMONTHDAY


	MONTHDAYYEARRANGE -> MONTHDAY TO DAY ocommadotsp YADPRECISEYEAR


	TIMENAME -> antiquity
	antiquity -> 'a' 'n' 't' 'i' 'q' 'u' 'i' 't' 'y'


	CA -> c a | c | about | '~' | MODIFIER

	BC -> b c | b c e
	AD -> a d | c e

	b -> 'b' | 'b' x
	c -> 'c' | 'c' x
	e -> 'e' | 'e' x
	a -> 'a' | 'a' x
	d -> 'd' | 'd' x
	x -> '.'
	s -> 's'

	early -> 'e' 'a' 'r' 'l' 'y'
	mid -> 'm' 'i' 'd'
	late -> 'l' 'a' 't' 'e'
	prior -> 'p' 'r' 'i' 'o' 'r'
	before -> 'b' 'e' 'f' 'o' 'r' 'e'
	after -> 'a' 'f' 't' 'e' 'r'
	RAWMODIFIER -> early | mid | late | prior sp to | before | after
	MODIFIER -> RAWMODIFIER | RAWMODIFIER osp dash osp

	q -> '?'
	dash -> '-' | '–' | '—'
	sp -> sp ' ' | ' '
	osp -> sp | 
	comma -> ','
	ocomma -> comma | 
	ocommadotsp -> comma osp | x osp | sp
	odashsp -> dash | osp

	n -> '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'

	about -> 'a' 'b' 'o' 'u' 't'
	to -> 't' 'o'
	years -> 'y' 'e' 'a' 'r' 's' | 'y' 'r' 's' | 'y' 'r' 's' x
	ago -> 'a' 'g' 'o'
	thousand -> 't' 'h' 'o' 'u' 's' 'a' 'n' 'd'
	million -> 'm' 'i' 'l' 'l' 'i' 'o' 'n'
	bp -> 'b' 'p'
	ma -> 'm' 'a'
	ka -> 'k' 'a'
	pm -> '±'
	th -> 't' 'h' | 's' 't' | 'n' 'd' | 'r' 'd'
	century -> 'c' 'e' 'n' 't' 'u' 'r' 'y'
	millenium -> 'm' 'i' 'l' 'l' 'e' 'n' 'i' 'u' 'm' | 'm' 'i' 'l' 'l' 'e' 'n' 'n' 'i' 'u' 'm'
 
	jan -> 'j' 'a' 'n' | 'j' 'a' 'n' x | 'j' 'a' 'n' 'u' 'a' 'r' 'y'
	feb -> 'f' 'e' 'b' | 'f' 'e' 'b' x | 'f' 'e' 'b' 'r' 'u' 'a' 'r' 'y'
	mar -> 'm' 'a' 'r' | 'm' 'a' 'r' x | 'm' 'a' 'r' 'c' 'h'
	apr -> 'a' 'p' 'r' | 'a' 'p' 'r' x | 'a' 'p' 'r' 'i' 'l'
	may -> 'm' 'a' 'y'
	jun -> 'j' 'u' 'n' | 'j' 'u' 'n' x | 'j' 'u' 'n' 'e'
	jul -> 'j' 'u' 'l' | 'j' 'u' 'l' x | 'j' 'u' 'l' 'y'
	aug -> 'a' 'u' 'g' | 'a' 'u' 'g' x | 'a' 'u' 'g' 'u' 's' 't'
	sep -> 's' 'e' 'p' | 's' 'e' 'p' x | 's' 'e' 'p' 't' | 's' 'e' 'p' 't' x | 's' 'e' 'p' 't' 'e' 'm' 'b' 'e' 'r'
	oct -> 'o' 'c' 't' | 'o' 'c' 't' x | 'o' 'c' 't' 'o' 'b' 'e' 'r'
	nov -> 'n' 'o' 'v' | 'n' 'o' 'v' x | 'n' 'o' 'v' 'e' 'm' 'b' 'e' 'r'
	dec -> 'd' 'e' 'c' | 'd' 'e' 'c' x | 'd' 'e' 'c' 'e' 'm' 'b' 'e' 'r'
	"""

date_grammar_words = [
	u'antiquity',
	u'early', u'mid', u'late', u'prior', u'before', u'after',
	u'about',
	u'to',
	u'years', u'yrs', u'ago', u'bp',
	u'ma', u'ka', u'thousand', u'million',
	u'th', u'st', u'nd', u'rd',
	u'century',
	u'millenium', 'millennium',
	u'ca',
	u'bc', u'bce', u'ad', u'ce',
	u'a', u'b', u'c', u'd', u'e',
	u's',
	u'jan', u'january', u'feb', u'february', u'mar', u'march',
	u'apr', u'april', u'may', u'jun', u'june', u'jul', u'july',
	u'aug', u'august', u'sep', u'sept', u'september',
	u'oct', u'october', u'nov',u'november', u'dec', u'december',
]

date_valid_nonwords_re_string = ur'^[\d,±\.\?/\-–—~ ]*$'
# the subset of characters that are valid in a date string that can also be a
# character that ends the date string
date_valid_end_char = ur'^[,\.\?\-–— ]$'