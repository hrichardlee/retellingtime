# -*- coding: UTF-8 -*-
date_grammar_string = u"""
	S -> DATE | YEARSAGO | DATERANGE

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

	DATERANGE -> DATE TO DATE | NUM TO DATE | ORD TO DATE

	TO -> osp dash osp | sp to sp

	PERIOD -> ORD osp century | ORD osp millenium
	ORD -> NUM th

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
	u'a', u'b', u'c', u'd', u'e'
]

date_valid_nonwords_re_string = ur'^[\d,±\.\?\-–— ]*$'