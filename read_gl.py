# coding: utf-8
import bs4, omnidoc

# TODOS:
# - fix completion / signature

name = 'OpenGL'
prefix = 'gl'

BASE_URL = 'http://www.opengl.org/sdk/docs/man/xhtml/'
PAGE_URL_FORMAT = BASE_URL + '{0}.xml'

def get_index():
	soup = bs4.BeautifulSoup(omnidoc.urlopen(BASE_URL).read())
	for link in soup('a', target='pagedisp'):
		name = link.get_text()
		yield omnidoc.Entry(
				label=name,
				desc=None,
				action=omnidoc.Navigate(prefix+':'+name)
			)

def header(title, hint, completion, doc_url): # TODO refactor out
	yield omnidoc.Entry(
		label=title, # TODO centering???
		desc=hint,
		action=omnidoc.Insert(completion))
	yield omnidoc.Entry(
		label='(show doc?)',
		desc=doc_url,
		action=omnidoc.OpenBrowser(doc_url))

def get_page(name):
	doc_url = PAGE_URL_FORMAT.format(name)
	soup = bs4.BeautifulSoup(omnidoc.urlopen(doc_url).read())
	title, _, desc = soup.find(class_='refnamediv').p.get_text().partition(u'—')
	title, desc = map(unicode.strip, (title, desc))
	completion = soup.find('div', class_='funcsynopsis').get_text()

	for k in header(title, desc, completion, doc_url):
		yield k

	variablelist = soup.find(class_='variablelist')	
	if variablelist:

		yield omnidoc.Entry(
			label=omnidoc.whitespace.pad+'Parameters:',
			desc=None,
			action=None)

		for dt in variablelist.dl.find_all('dt', recursive=False):
			dd = dt.find_next_sibling('dd')
			name, desc = dt.get_text().strip(), dd.get_text().strip()
			# OGL is a bit crazy with spaces, so
			name = ' '.join(name.split())
			desc = ' '.join(desc.split())
			yield omnidoc.Entry(name, desc, omnidoc.Insert(name))


omnidoc.create_module(**locals())
