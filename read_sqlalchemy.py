# coding: utf-8
import bs4, omnidoc

name = 'SQLAlchemy'
prefix = 'sqla'

def get_index():
	yield omnidoc.Entry(label='Query', desc=None, action=omnidoc.Navigate('%s:%s' % (prefix,'Query')))
	
def get_page(name):
	query = bs4.BeautifulSoup(omnidoc.urlopen('http://docs.sqlalchemy.org/en/rel_0_8/orm/query.html'))
	for m in query('dl', class_='method'):
		name = m.find(class_='descname').get_text()
		sig = m.dt.get_text().strip().rstrip(u'\xb6')
		desc = omnidoc.wrap(m.dd.find('p').get_text().replace('\n',' '))
		yield omnidoc.Entry(label=name, desc=[sig]+desc, action=omnidoc.Insert(sig))

omnidoc.create_module(**locals())
