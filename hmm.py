'''This module loads stuff from python.org'''

from bs4 import BeautifulSoup

with open('snippets/python.txt') as f:
	testdata = f.read()
with open('snippets/python3.txt') as f:
	testdata3 = f.read()

soup = BeautifulSoup(testdata)

import collections
MehPage = collections.namedtuple('MehPage','label name url action') # deprecated

def indexPage():
	''' Returns a list of entries.
	Each entry has a label, name, url'''

	base_url = 'http://docs.python.org/2/library/'
	def url_matches(url):
		return url.endswith('.html') and url[:-5].isalpha()
	links = soup('a', class_="reference internal", href=url_matches)
	return [MehPage(
			label=a.get_text(),
			url=base_url+a['href'],
			name=a['href'][:-5],
			action=None
		) for a in links]
	return links


def testPage():

	soup = BeautifulSoup(testdata3)

	for defs in 'dam sobie spokoj':
		pass







xx = indexPage()

f = [tup for tup in xx
	if tup.label == '13. File Formats' and tup.name == 'fileformats' and tup.url == 'http://docs.python.org/2/library/fileformats.html']

ff = [tup for tup in xx
	if 'stdtypes' in tup.url]

assert len(f) == 1
assert len(ff) == 1


print 'yay'