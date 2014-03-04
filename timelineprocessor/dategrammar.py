# -*- coding: UTF-8 -*-
date_grammar_string = u"""
	S -> MONTH | MONTHDAY | DATE | YEARSAGO | DATERANGE


	YEARSAGO -> YAS | YAR | MAS | MAR

	YAS -> NUM osp years sp ago
	YAR -> NUM TO NUM osp years sp ago

	MAS -> DEC osp ma ago | DEC osp ma
	MAR -> DEC TO DEC ma ago | DEC TO DEC osp ma

	NUM -> NUME | NUMQ
	NUME -> NUMLEADGROUP NUMGROUPS
	NUMQ -> CA osp NUME | NUME q
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
	PERIODBC -> PERIOD osp BC
	YAD -> NUM osp AD | NUM
	PERIODAD ->  PERIOD osp AD | PERIOD

	PERIOD -> ORD osp century | ORD osp millenium
	ORD -> NUM th


	DATERANGE -> DATE TO DATE | ORD TO DATE

	TO -> osp dash osp | sp to sp


	MONTH -> jan | feb | march | apr | may | jun | jul | aug | sep | oct | nov | dec

	DAY -> n | '0' n | '1' n | '2' n | '3' '0' | '3' '1'

	MONTHDAY -> DAY sp MONTH | MONTH ocomma sp DAY


	CA -> c a | c | about

	BC -> b c | b c e
	AD -> a d | c e

	b -> 'b' | 'b' x
	c -> 'c' | 'c' x
	e -> 'e' | 'e' x
	a -> 'a' | 'a' x
	d -> 'd' | 'd' x
	x -> '.'

	q -> '?'
	dash -> '-' | '–' | '—'
	sp -> sp ' ' | ' '
	osp -> sp | 
	comma -> ','
	ocomma -> ',' | 

	n -> '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'

	about -> 'a' 'b' 'o' 'u' 't'
	to -> 't' 'o'
	years -> 'y' 'e' 'a' 'r' 's' | 'y' 'r' 's' | 'y' 'r' 's' x
	ago -> 'a' 'g' 'o'
	ma -> 'm' 'a'
	pm -> '±'
	th -> 't' 'h' | 's' 't' | 'n' 'd' | 'r' 'd'
	century -> 'c' 'e' 'n' 't' 'u' 'r' 'y'
	millenium -> 'm' 'i' 'l' 'l' 'e' 'n' 'i' 'u' 'm' | 'm' 'i' 'l' 'l' 'e' 'n' 'n' 'i' 'u' 'm'

	jan -> 'j' 'a' 'n' | 'j' 'a' 'n' 'u' 'a' 'r' 'y'
	feb -> 'f' 'e' 'b' | 'f' 'e' 'b' 'r' 'u' 'a' 'r' 'y'
	mar -> 'm' 'a' 'r' | 'm' 'a' 'r' 'c' 'h'
	apr -> 'a' 'p' 'r' | 'a' 'p' 'r' 'i' 'l'
	may -> 'm' 'a' 'y'
	jun -> 'j' 'u' 'n' | 'j' 'u' 'n' 'e'
	jul -> 'j' 'u' 'l' | 'j' 'u' 'l' 'y'
	aug -> 'a' 'u' 'g' | 'a' 'u' 'g' 'u' 's' 't'
	sep -> 's' 'e' 'p' | 's' 'e' 'p' 't' | 's' 'e' 'p' 't' 'e' 'm' 'b' 'e' 'r'
	oct -> 'o' 'c' 't' | 'o' 'c' 't' 'o' 'b' 'e' 'r'
	nov -> 'n' 'o' 'v' | 'n' 'o' 'v' 'e' 'm' 'b' 'e' 'r'
	dec -> 'd' 'e' 'c' | 'd' 'e' 'c' 'e' 'm' 'b' 'e' 'r'
	"""

date_grammar_words = [
	u'about',
	u'to',
	u'years', u'yrs', 
	u'ago',
	u'ma',
	u'th', u'st', u'nd', u'rd',
	u'century',
	u'millenium', 'millennium',
	u'ca',
	u'bc', u'bce', u'ad', u'ce',
	u'a', u'b', u'c', u'd', u'e',
	u'jan', u'january', u'feb', u'february', u'mar', u'march',
	u'apr', u'april', u'may', u'jun', u'june', u'jul', u'july',
	u'aug', u'august', u'sep', u'sept', u'september',
	u'oct', u'october', u'nov',u'november', u'dec', u'december',
]

date_valid_nonwords_re_string = ur'^[\d,±\.\?\-–— ]*$'
# the subset of characters that are valid in a date string that can also be a
# character that ends the date string
date_valid_end_char = ur'^[,\.\?\-–— ]$'