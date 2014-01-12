from bs4 import BeautifulSoup
import bs4
import copy

import pdb

class HtmlSplitter:
	"""Initialize with an html string, and then call get_span to get the html
	strings that correspond to text-only strings.
	"""

	def __init__(self, html_string):
		# constructs a list of ranges where a range is {"el": soup, "range":
		# (a, b)} and each range corresponds to a top-level element of
		# htmlString. The range indicates which elements to look in for which
		# ranges of text
		soup = BeautifulSoup(html_string)
		self.text_string = soup.get_text()

		if len(soup.contents) > 1:
			top_level_ranges = [{"el": el, "range": None} for el in soup.contents]
			i = 0
			for r in self._get_text_indices(soup):
				# get the top-level parent element
				# r["el"] should never be the top level element (implying
				# len(parents) == 0) because _get_text_indices always processes
				# starting with the nodes immediately under the root
				parents = list(r["el"].parents)
				top_level_el = r["el"] if len(parents) == 1 else parents[-2]
				while id(top_level_ranges[i]["el"]) != id(top_level_el):
					i += 1
				top_level_range = top_level_ranges[i]
				
				# modify the range for that top-level element
				if top_level_range["range"]:
					top_level_range["range"] = (min(top_level_range["range"][0], r["range"][0]),
						max(top_level_range["range"][1], r["range"][1]))
				else:
					top_level_range["range"] = r["range"]

			# finally, check for top-level elements that do not contain any
			# text and thus do not have ranges
			for r, prevr in zip(top_level_ranges, [{"el": None, "range": (0, 0)}] + top_level_ranges):
				if not r["range"]:
					r["range"] = (prevr["range"][1], prevr["range"][1])
		else:
			# the actual text is probably much smaller than html_string, but we
			# just need an upper bound
			top_level_ranges = [{"el": soup.contents[0], "range": (0, len(html_string))}]
		self._top_level_ranges = top_level_ranges

	def _get_text_indices(self, soup):
		"""Given a soup, returns a list of ranges = [{range: (a, b), el:
		NavigableString}, ...] where each bs4.NavigableString in the original
		soup corresponds to an item in the list. The range that is associated
		with each NavigableString represents the range in the text-only string
		of the original soup that corresponds to that NavigableString
		"""
		(ranges, _) = self._get_text_indices_helper(soup, 0)
		return ranges

	def _get_text_indices_helper(self, soup, index):
		if isinstance(soup, bs4.NavigableString):
			return ([{"range": (index, index + len(soup)), "el": soup}],
				index + len(soup))
		else:
			ranges = []
			for el in soup.children:
				(new_ranges, new_index) = self._get_text_indices_helper(el, index)
				index = new_index
				ranges += new_ranges
			return (ranges, index)

	def _get_applicable_ranges(self, ranges, start, end):
		"""Given a list of ranges = [{range: (a, b), el: soup}, ...], and
		(start, end), returns a list of ranges that overlap with (start, end).
		Assumes that ranges is sorted ascending by range and is contiguous.
		"""
		applicable_ranges = []
		for r in ranges:
			if r["range"][1] > start:
				if r["range"][0] < end:
					applicable_ranges.append(r)
				else:
					break
		return applicable_ranges


	def _modify_ranges(self, ranges, start = None, end = None):
		"""Given a list of ranges, and (start, end), modifies the elements
		referenced by ranges such that only the text corresponding to (start,
		end) remains. If start or end are None, then assumes that start is 0
		and end is infinity. Assumes ranges is non-empty
		"""

		def remove_siblings(el, direction):
			"""Direction must be "prev" or "next"
			"""
			if el:
				siblings = el.previous_siblings if direction == "prev" else el.next_siblings
				for sib in list(siblings):
					sib.extract()
				remove_siblings(el.parent, direction)

		# remove text from before the first and after the last element
		if start != None: remove_siblings(ranges[0]["el"], "prev")
		if end != None: remove_siblings(ranges[-1]["el"], "next")

		# replace text within element
		if len(ranges) == 1 and start and end:
			offset = ranges[0]["range"][0]
			ranges[0]["el"].replace_with(ranges[0]["el"][start - offset:end - offset])
		else:
			if start:
				offset = ranges[0]["range"][0]
				ranges[0]["el"].replace_with(ranges[0]["el"][start - offset:])
			# this causes somewhat weird behavior when there's an image or something at the end of an element
			if end:
				offset = ranges[-1]["range"][0]
				ranges[-1]["el"].replace_with(ranges[-1]["el"][:end - offset])


	def get_span(self, start, end):
		"""Given indices (start, end) in the pure-text version of the
		htmlString this object is initialized with, returns the html string
		that corresponds to the specified text string
		"""

		# we need to copy so that we don't destroy self._top_level_ranges
		top_level_ranges = [copy.deepcopy(r) \
		 for r in self._get_applicable_ranges(self._top_level_ranges, start, end)]

		# create a new top-level soup so that we can modify elements in place
		result = BeautifulSoup()
		for r in top_level_ranges:
			r["el"] = r["el"].extract()
			result.append(r["el"])

		if len(top_level_ranges) == 1:
			range_offset = top_level_ranges[0]["range"][0]
			inner_start = start - range_offset
			inner_end = end - range_offset

			self._modify_ranges(self._get_applicable_ranges(
					self._get_text_indices(top_level_ranges[0]["el"]),
					inner_start, inner_end),
				inner_start, inner_end)
		else:
			range_offset = top_level_ranges[0]["range"][0]
			inner_start = start - range_offset
			inner_end = end - range_offset

			self._modify_ranges(
				self._get_applicable_ranges(
					self._get_text_indices(top_level_ranges[0]["el"]),
					inner_start, inner_end),
				start = inner_start)

			range_offset = top_level_ranges[-1]["range"][0]
			inner_start = start - range_offset
			inner_end = end - range_offset

			self._modify_ranges(
				self._get_applicable_ranges(
					self._get_text_indices(top_level_ranges[-1]["el"]),
					inner_start, inner_end),
				end = inner_end)

		return result