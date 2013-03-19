import sublime, sublime_plugin
import webbrowser, threading

# Initialise the module dictionaries, but don't overwrite upon reload()

if 'modules_by_prefix' not in locals():
    modules_by_prefix = {}
if 'modules_by_name' not in locals():
    modules_by_name = {}

# TODOS:
# - page caching :o
# - read some input from buffer and use it as a query

def create_module(**kwargs):
    register_module(Module(**kwargs))

def register_module(mod):
    modules_by_prefix[mod.prefix] = mod
    modules_by_name[mod.name] = mod

class Module(object):
    required_stuff = ['name', 'prefix', 'get_index', 'get_page']

    def __init__(self, **kwargs):
        for field in self.required_stuff:
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
Entry = collections.namedtuple('Entry','label desc action')

def wrap(s, maxlines=3, shorten=0):
    maxlines = maxlines - shorten
    import textwrap
    wrapped = textwrap.wrap(s, 70)
    if len(wrapped) > maxlines:
        wrapped = wrapped[:maxlines]
        wrapped[-1] = wrapped[-1][:55] + '...'
    return wrapped

def entry2item(entry):
    if entry.desc is None:
        return entry.label
    if isinstance(entry.desc, (list, tuple)):
        # we're iterable, don't wrap
        return [entry.label] + list(entry.desc)
    else:
        # consider desc a string, wrap if needed
        return [entry.label] + wrap(entry.desc)

class whitespace:
    pad = ' '*8
    pad2 = ' ' * 10
    center = pad*2
    center2 = pad2*2

class OmnidocCommand(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        '''Plug-in entry point.'''
        self.wnd = self.view.window()
        self.edit = edit

        # For now, start with calling the module list
        # TODO: read some context and decide
        self.show_modules()

    def navigate(self, module, page=None):
        '''navigate(module, page) - Retrieves and displays a specific page from a module'''

        # TODO attempt to retrieve from cache first

        def threadfunc():
            error = None
            try:
                if not page:
                    entries = module.get_index()
                else:
                    entries = module.get_page(page)

                # Unwind any generators.
                if iter(entries) is entries:
                    entries = list(entries)
            except Exception, e:
                import traceback
                print traceback.format_exc()
                error = str(e)

            # Go back to main thread with result
            def done():
                if error:
                    self.show_error_message(error)
                else:
                    self.show_entries(entries)
            sublime.set_timeout(done, 0)
        
        t = threading.Thread(target=threadfunc, name='fetch doc thread')
        t.start()

    def navigate_by_prefix(self, moduleprefix, page):
        module = modules_by_prefix[moduleprefix]
        self.navigate(module, page)

    def show_entries(self, entries):
        '''show_entries( [Entry] ) - opens a quick panel with specified entries'''
        entries = list(entries)
        items = map(entry2item, entries)

        def on_done(n):
            if n<0: return
            action = entries[n].action
            if action:
                action(self)
            
        self.wnd.show_quick_panel(items, on_done, 0)


    def show_modules(self):
        '''Lists available modules'''
        entries = []
        for name, mod in sorted(modules_by_name.iteritems(), key=lambda (name, mod): name):
            entry = Entry(label=mod.name,
                desc='TODO description',
                action=Navigate(mod.prefix))
            entries.append(entry)
        if len(entries) == 0:
            entries.append(Entry(label="No modules found :(", desc=None, action=None))
        self.show_entries(entries)


    def show_error_message(self, msg):
        # This cool enough?
        sublime.status_message(msg)

    # Action callbacks

    def action_navigate(self, page):
        module,_,pagename = page.partition(':')
        return self.navigate_by_prefix(module, pagename)

    def action_write(self, text):
        for region in self.view.sel():
            self.view.insert(self.edit, region.end(), text)

