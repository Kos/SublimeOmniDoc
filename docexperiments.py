import sublime, sublime_plugin
import webbrowser, threading
from registered import modules_by_name, modules_by_prefix

# TODOS:
# - some renames (page, this module itself...)
# - caching :o
# - read some input from buffer
# - cleanup register_module / Module

def register_module(mod): # Naaaaaaaaah,
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

    def run(self, edit, **kwargs):
        '''Plug-in entry point.'''
        self.wnd = self.view.window()
        self.edit = edit

        # For now, start with calling the command list
        # TODO: read some context and decide
        self.show_modules()

    def navigate(self, module, page=None):
        '''navigate(module, page) - Retrieves and displays a specific page from a module'''

        # TODO attempt to retrieve from cache first

        def threadfunc():
            error = None
            try:
                if not page:
                    pages = module.index()
                else:
                    pages = module.page(page)

                # Unwind any generators.
                if iter(pages) is pages:
                    pages = list(pages)
            except Exception, e:
                import traceback
                print traceback.format_exc()
                error = str(e)

            # Go back to main thread with result
            def done():
                if error:
                    self.show_error_message(error)
                else:
                    self.show_pages(pages)
            sublime.set_timeout(done, 0)
        
        t = threading.Thread(target=threadfunc, name='fetch doc thread')
        t.start()

    def navigate_by_prefix(self, moduleprefix, page):
        module = modules_by_prefix[moduleprefix]
        self.navigate(module, page)

    def show_pages(self, pages):
        '''show_pages( [Page] ) - opens a quick panel with specified pages'''
        pages = list(pages)
        items = map(page2item, pages)

        def on_done(n):
            if n<0: return
            action = pages[n].action
            if action:
                action(self)
            
        self.wnd.show_quick_panel(items, on_done, 0)


    def show_modules(self):
        '''Lists available modules'''
        pages = []
        for name, mod in sorted(modules_by_name.iteritems(), key=lambda (name, mod): name):
            item = Page(label=mod.name,
                desc='TODO description',
                action=Navigate(mod.prefix))
            pages.append(item)
        if len(pages) == 0:
            pages.append(Page(label="No modules found :(", desc=None, action=None))
        self.show_pages(pages)


    def show_error_message(self, msg):
        # This cool enough?
        sublime.status_message(msg)

    # Action callbacks

    def action_navigate(self, page):
        module,_,page = page.partition(':')
        return self.navigate_by_prefix(module, page)

    def action_write(self, text):
        for region in self.view.sel():
            self.view.insert(self.edit, region.end(), text)

