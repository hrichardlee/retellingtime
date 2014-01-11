# -*- coding: UTF-8 -*-

import wikipedia
import wikipediaprocess
from bs4 import BeautifulSoup
import unittest
import json
from pprint import pprint

htmlone = """<h2><span class="mw-headline" id="Progressive_Era_.281890.E2.80.931919.29"><a href="/wiki/Progressive_Era" title="Progressive Era">Progressive Era</a> (1890–1919)</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_United_States_inventions_(1890%E2%80%931945)&amp;action=edit&amp;section=1" title="Edit section: Progressive Era (1890–1919)">edit</a><span class="mw-editsection-bracket">]</span></span></h2>
<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>
<p>A stop sign is a traffic sign, ...<sup id="cite_ref-13" class="reference"><a href="#cite_note-13"><span>[</span>13<span>]</span></a></sup></p>
<p><b>1890 <a href="/wiki/Tabulating_machine" title="Tabulating machine">Tabulating machine</a></b></p>
<p>The tabulating machine is an ...</p>
<h2><span class="mw-headline" id="Progressive_Era_.281890.E2.80.931919.29"><a href="/wiki/Progressive_Era" title="Progressive Era">Progressive Era</a> (1890–1919)</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_United_States_inventions_(1890%E2%80%931945)&amp;action=edit&amp;section=1" title="Edit section: Progressive Era (1890–1919)">edit</a><span class="mw-editsection-bracket">]</span></span></h2>
<p><b>1890 <a href="/wiki/Shredded_wheat" title="Shredded wheat">Shredded wheat</a></b></p>
<ul>
<li>Shredded wheat is a type of breakfast cereal made from whole <a href="/wiki/Wheat" title="Wheat">wheat</a>. Shredded wheat also comes in a <i>frosted</i> variety,...</li>
</ul>"""
stringblocksone = [[u'<b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>',
			u'A stop sign is a traffic sign, ...<sup class="reference" id="cite_ref-13"><a href="#cite_note-13"><span>[</span>13<span>]</span></a></sup>',
			u'<b>1890 <a href="/wiki/Tabulating_machine" title="Tabulating machine">Tabulating machine</a></b>',
			u'The tabulating machine is an ...'],
			[u'<b>1890 <a href="/wiki/Shredded_wheat" title="Shredded wheat">Shredded wheat</a></b>',
			u'Shredded wheat is a type of breakfast cereal made from whole <a href="/wiki/Wheat" title="Wheat">wheat</a>. Shredded wheat also comes in a <i>frosted</i> variety,...'			]]
htmltwo = """<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>
<p>A stop sign is a traffic sign, ...<sup id="cite_ref-13" class="reference"><a href="#cite_note-13"><span>[</span>13<span>]</span></a></sup></p>
<p><b>1890 <a href="/wiki/Tabulating_machine" title="Tabulating machine">Tabulating machine</a></b></p>
<p>The tabulating machine is an ...</p>"""
stringblockstwo = [[u'<b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>',
			u'A stop sign is a traffic sign, ...<sup class="reference" id="cite_ref-13"><a href="#cite_note-13"><span>[</span>13<span>]</span></a></sup>',
			u'<b>1890 <a href="/wiki/Tabulating_machine" title="Tabulating machine">Tabulating machine</a></b>',
			u'The tabulating machine is an ...']]

class TestExtractTimeline(unittest.TestCase):
	def testExtractTimeline(self):
		data = wikipediaprocess.extractTimeline(wikipedia.page('Timeline of particle physics'))
		print data
		with open('particlephysics.json', 'w') as f:
			f.write(json.dumps(data))

class TestStringsToEvents(unittest.TestCase):
	def testOne(self):
		pprint(wikipediaprocess.stringsToEvents(stringblocksone))

class TestGetStringBlocks(unittest.TestCase):
	def testOne(self):
		html = BeautifulSoup(htmlone)
		strings = wikipediaprocess.getStringBlocks(html)
		self.assertEqual(strings, stringblocksone)

	def testTwo(self):
		html = BeautifulSoup(htmltwo)
		strings = wikipediaprocess.getStringBlocks(html)
		self.assertEqual(strings, stringblockstwo)

class TestFindDate(unittest.TestCase):
	def setUp(self):
		self.nolayer = '1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		self.onelayer = '<b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>'
		self.twolayers = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>'
		self.threelayers = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>blergh</p>'
		self.remainder = '<a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		self.remainderthreelayers = '<a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>blergh'

	def testOne(self):
		(x, y) = wikipediaprocess.getFirstPart(BeautifulSoup(self.onelayer))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess.findDate(self.onelayer)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)
	def testTwo(self):
		(x, y) = wikipediaprocess.getFirstPart(BeautifulSoup(self.nolayer))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess.findDate(self.nolayer)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)
	def testThree(self):
		(x, y) = wikipediaprocess.getFirstPart(BeautifulSoup(self.twolayers))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess.findDate(self.twolayers)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)
	def testFour(self):
		(x, y) = wikipediaprocess.getFirstPart(BeautifulSoup(self.threelayers))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainderthreelayers)
		(x, y) = wikipediaprocess.findDate(self.threelayers)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainderthreelayers)

if __name__ == '__main__':
	unittest.main()
