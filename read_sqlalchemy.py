# coding: utf-8
import bs4, omnidoc, string

name = 'SQLAlchemy'
prefix = 'sqla'

pages = []
pages_dict = {}

def page(name, desc):
	def decorate(func):
		pages.append((name, desc, func))
		pages_dict[name] = func
		return func
	return decorate

def get_index():
	return (omnidoc.Entry(label=name, desc=desc, action=omnidoc.Navigate('%s:%s' % (prefix,name))) for name, desc, func in pages)
	
def get_page(name):
	return pages_dict[name]()

@page('Query','class')
def get_page_query():
	query = bs4.BeautifulSoup(omnidoc.urlopen('http://docs.sqlalchemy.org/en/rel_0_8/orm/query.html'))
	return read_type(query)

@page('relation','function')
def get_page_relation():
	relationship = bs4.BeautifulSoup(omnidoc.urlopen('http://docs.sqlalchemy.org/en/rel_0_8/orm/relationships.html'))
	fieldlist = relationship.find(class_='field-list')
	return read_fieldlist(fieldlist)

@page('Column', 'class')
def get_page_column():
	column = bs4.BeautifulSoup(omnidoc.urlopen('http://docs.sqlalchemy.org/en/rel_0_8/core/schema.html'))
	parent = column.find('dt', id='sqlalchemy.schema.Column').parent
	return read_type(parent)	

@page('Column.__init__','constructor')
def get_page_column_init():
	column = bs4.BeautifulSoup(omnidoc.urlopen('http://docs.sqlalchemy.org/en/rel_0_8/core/schema.html'))
	fieldlist = column.find('dt', id='sqlalchemy.schema.Column.__init__').parent.find('table',class_='field-list')
	return read_fieldlist(fieldlist)


def read_fieldlist(fieldlist):
	for li in fieldlist.ul.find_all('li', recursive=False):
	    name, _, default = li.strong.get_text().partition('=')
	    if li.p:
	        desc = li.p.get_text()
	    else:
	        trim = len(li.strong.get_text())
	        desc = li.get_text()[trim:].strip(string.whitespace+u'–')
	    yield omnidoc.Entry(label=name, desc=desc, action=omnidoc.Insert(name))

def read_type(elem):
	for m in elem('dl'):
		name = m.find(class_='descname').get_text()
		sig = m.dt.get_text().strip().rstrip(u'\xb6')
		desc_p = m.dd.find('p')
		desc = omnidoc.wrap(desc_p.get_text().replace('\n',' ')) if desc_p else []
		yield omnidoc.Entry(label=name, desc=[sig]+desc, action=omnidoc.Insert(sig))


omnidoc.create_module(**locals())
