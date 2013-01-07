# coding: utf-8
import docexperiments as gendoc
Page = gendoc.Page

# TODOS:
# - rename
# - fix completion / signature

TIMEOUT=5
from bs4 import BeautifulSoup
import urllib2

NAMESPACE = 'gl'
BASE_URL = 'http://www.opengl.org/sdk/docs/man/xhtml/'
PAGE_URL_FORMAT = BASE_URL + '{0}.xml'

def index():
	page = urllib2.urlopen(BASE_URL, timeout=TIMEOUT).read()
	soup = BeautifulSoup(page)
	for link in soup('a', target='pagedisp'):
		name = link.get_text()
		yield gendoc.Page(
				label=name,
				desc=None,
				action=gendoc.Navigate(NAMESPACE+':'+name)
			)

def header(title, hint, completion, doc_url):
	yield Page(
		label=title, # TODO centering
		desc=hint,
		action=gendoc.Insert(completion))
	yield Page(
		label='(show doc?)',
		desc=doc_url,
		action=gendoc.OpenBrowser(doc_url))

def page(name):

	doc_url = PAGE_URL_FORMAT.format(name)
	print 'would read', doc_url
	page = urllib2.urlopen(doc_url, timeout=TIMEOUT).read()
	soup = BeautifulSoup(page) # TODO fetch page
	title, _, desc = soup.find(class_='refnamediv').p.get_text().partition(u'—')
	title, desc = map(unicode.strip, (title, desc))
	completion = soup.find(summary='Function synopsis').get_text()

	for k in header(title, desc, completion, doc_url):
		yield k



	yield Page(
		label='Parameters:',
		desc=None,
		action=None)

	for dt in soup.find(class_='variablelist').dl.find_all('dt', recursive=False):
		dd = dt.find_next_sibling('dd')
		name, desc = dt.get_text().strip(), dd.get_text().strip()
		yield Page(name, desc, gendoc.Insert(name))

module = gendoc.Module(name='OpenGL', prefix='gl', **locals())
gendoc.register_module(module)
