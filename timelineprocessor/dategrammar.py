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

	CA -> c a | c

	BC -> b c | b c e
	AD -> a d | c e

	TO -> osp dash osp | sp to sp

	PERIOD -> ORD osp century | ORD osp millenium
	ORD -> NUM th

	b -> 'b' | 'b' x
	c -> 'c' | 'c' x
	e -> 'e' | 'e' x
	a -> 'a' | 'a' x
	d -> 'd' | 'd' x
	x -> '.'

	q -> '?'
	dash -> '-' | '–' | '—'
	to -> 't' 'o'
	n -> '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
	sp -> sp ' ' | ' '
	osp -> sp | 
	comma -> ','
	years -> 'y' 'e' 'a' 'r' 's' | 'y' 'r' 's' | 'y' 'r' 's' x
	ago -> 'a' 'g' 'o'
	ma -> 'm' 'a'
	pm -> '±'
	th -> 't' 'h' | 's' 't' | 'n' 'd' | 'r' 'd'
	century -> 'c' 'e' 'n' 't' 'u' 'r' 'y'
	millenium -> 'm' 'i' 'l' 'l' 'e' 'n' 'i' 'u' 'm' | 'm' 'i' 'l' 'l' 'e' 'n' 'n' 'i' 'u' 'm'
	"""