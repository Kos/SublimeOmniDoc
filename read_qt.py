# coding: utf-8
import bs4, omnidoc

name = 'Qt framework'
prefix = 'qt'
index_url = 'http://qt-project.org/doc/qt-4.8/classes.html'
page_url_format = 'http://qt-project.org/doc/qt-4.8/{0}.html'

def get_index():
	soup = bs4.BeautifulSoup(omnidoc.urlopen(index_url))
	for dd in soup.find('div',class_='descr').find_all('dd'):
		a = dd.a
		if a is None:
			continue
		yield omnidoc.Entry(label=a.get_text().strip(), desc=None, action=omnidoc.Navigate(prefix+':'+a['href'][:-5]))


def header(title, hint, completion, doc_url): # TODO refactor out
	yield omnidoc.Entry(
		label=title, # TODO centering
		desc=hint,
		action=omnidoc.Insert(completion))
	yield omnidoc.Entry(
		label='(show doc?)',
		desc=doc_url,
		action=omnidoc.OpenBrowser(doc_url))

def find_desc_para(elem):
	'''Finds the first paragraph after elem, but no further than a h3'''
	elem = elem.next_sibling
	while elem is not None:
		if isinstance(elem, bs4.Tag):
			if elem.name == 'p':
				return elem
			if elem.name == 'h3':
				return None
		elem = elem.next_sibling

def h3_to_page(h3, parentname):
	name = h3.find('span', class_='name').get_text().strip()
	sig = h3.get_text().strip()
	# get the class name out of here, it's clutter
	sig = sig.replace(parentname+'::', '')
	description = find_desc_para(h3).get_text().strip()
	completion = sig # TODO a better completion
	return omnidoc.Entry(label=name, desc=[sig]+omnidoc.wrap(description, shorten=1), action=omnidoc.Insert(completion))

def get_page(name):
	soup = bs4.BeautifulSoup(omnidoc.urlopen(page_url_format.format(name)))
	title, hint = soup.title.get_text().partition('|')[2].strip().split()[:2]
	for k in header(
			title = title,
			hint = hint,
			completion = title,
			doc_url = page_url_format.format(name)):
		yield k
	for h3 in soup.find('div', class_='func').find_all('h3', class_='fn'):
		yield h3_to_page(h3, title)

	#for li in soup.find('table',class_='propsummary').find_all('li',class_='fn'):

omnidoc.create_module(**locals())

