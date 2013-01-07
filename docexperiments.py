import sublime, sublime_plugin
sublime
import webbrowser, threading

# TODOS:
# - some renames (page, this module itself...)
# - caching :o
# - threading
# - read some input from buffer
# - handle read failures

modules_by_prefix = {}
modules_by_name = {}

def register_module(mod):
    modules_by_prefix[mod.prefix] = mod
    modules_by_name[mod.name] = mod

class Module(object):

    def __init__(self, **kwargs):
        for field in 'name prefix index page'.split():
            setattr(self, field, kwargs[field])

class Navigate(object):

    def __init__(self, page):
        self.page = page

    def __call__(self, plugin):
        plugin.action_navigate(self.page)


class OpenBrowser(object):

    def __init__(self, url):
        self.url = url

    def __call__(self, plugin):
        #print 'Would open browser at', self.url
        webbrowser.open_new_tab(self.url)

class Insert(object):

    def __init__(self, code):
        self.code = code

    def __call__(self, plugin):
        plugin.action_write(self.code)
                

import collections
Page = collections.namedtuple('Page','label desc action') # TODO rename me, should be like 'entry'


def wrap(s):
    maxlines = 3
    import textwrap
    wrapped = textwrap.wrap(s, 60)
    if len(wrapped) > maxlines:
        wrapped = wrapped[:maxlines]
        wrapped[-1] = wrapped[-1][:55] + '...'
    return wrapped

def page2item(page):
    if page.desc is None:
        return page.label
    if isinstance(page.desc, (list, tuple)):
        # we're iterable, don't wrap
        return [page.label] + list(page.desc)
    else:
        # consider desc a string, wrap if needed
        return [page.label] + wrap(page.desc)



def stuff___(wnd, view, edit):

    pad = ' '*8
    pad2 = ' ' * 10
    center = pad*2
    center2 = pad2*2

    center, center2

    [
        [pad+'Sublime','package'],
        ['(show doc?)','http://www.sublimetext.com/docs/2/api_reference.html'],
        [pad+'Members:'],
    ]


class FooCommand(sublime_plugin.TextCommand):

    def action_navigate(self, page):
        module,_,page = page.partition(':')
        return self.navigate_by_name(module, page)

    def action_write(self, text):
        for region in self.view.sel():
            self.view.insert(self.edit, region.end(), text)

    def navigate_by_name(self, modulename, page):
        import hmm2 as module
        self.navigate(module, page)

    def navigate(self, module, page=None):
        # find the correct module
        # import hmm2 as module

        if not page:
            pages = module.index()
        else:
            pages = module.page(page)

        self.show_pages(pages)

    def show_pages(self, pages):
        pages = list(pages)
        items = map(page2item, pages)

        def on_done(n):
            if n<0: return
            action = pages[n].action
            if action:
                action(self)
            
        self.wnd.show_quick_panel(items, on_done, 0)


    def commands(self):
        pages = []
        for name, mod in sorted(modules_by_name.iteritems(), key=lambda (name, mod): name):
            item = Page(label=mod.name,
                desc=['raz','dwa','trzy'],
                action=Navigate(mod.prefix))
            pages.append(item)
        if len(pages) == 0:
            pages.append(Page(label="No modules found :(", desc=None, action=None))
        self.show_pages(pages)



    def run(self, edit, **kwargs): # YES
        self.wnd = self.view.window()
        self.edit = edit
        self.commands()
        #self.navigate(module)
