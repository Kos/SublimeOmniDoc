import sublime, sublime_plugin
import webbrowser, threading, urllib2

# Initialise the module dictionaries, but don't overwrite upon reload()

if 'modules_by_prefix' not in locals():
    modules_by_prefix = {}
if 'modules_by_name' not in locals():
    modules_by_name = {}

# TODOS:
# - read some input from buffer and use it as a query

def urlopen(url, *what, **ever):
    def tell():
        sublime.status_message('OmniDoc: Retrieving {0}'.format(url))

    # Send the postcard to the main thread
    sublime.set_timeout(tell, 0) 
    # Run actual urlopen; errors are reported by callee
    return urllib2.urlopen(url, *what, **ever)
    

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
        plugin.navigate2(self.page)


class OpenBrowser(object):

    def __init__(self, url):
        self.url = url

    def __call__(self, plugin):
        webbrowser.open_new_tab(self.url)

class Insert(object):

    def __init__(self, code):
        self.code = code

    def __call__(self, plugin):
        view = plugin.view
        edit = plugin.edit # ?
        for region in view.sel():
            view.insert(edit, region.end(), self.code)
                

import collections
class Entry(collections.namedtuple('_Entry','label desc action')):
    '''Represents an item to be displayed in Sublime quick panel'''

    def as_list(self):
        '''
        returns an entry as understood by show_quick_panel:
        first line is the header, following lines contain the description
        '''
        if not self.desc:
            return [self.label]
        if isinstance(self.desc, (str, unicode)):
            description_lines = wrap(self.desc)
        else:
            description_lines = list(self.desc)
        return [self.label] + description_lines



def wrap(s, maxlines=3, shorten=0):
    maxlines = maxlines - shorten
    import textwrap
    wrapped = textwrap.wrap(s, 70)
    if len(wrapped) > maxlines:
        wrapped = wrapped[:maxlines]
        wrapped[-1] = wrapped[-1][:55] + '...'
    return wrapped


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

        try:
            self.show_entries(data_cache[module, page])
            return
        except KeyError:
            pass

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
                error = unicode(e)

            # Go back to main thread with result
            def done():
                if error:
                    self.show_error_message("Can't retrieve page {0}: {1}".format(page, error))
                else:
                    data_cache[module, page] = entries
                    self.show_entries(entries)
            sublime.set_timeout(done, 0)
        
        t = threading.Thread(target=threadfunc, name='fetch doc thread')
        t.start()

    def navigate2(self, qualified_page):
        '''navigate2(qualified_page) - reads "module:page" and calls navigate'''
        module_prefix, _, page = qualified_page.partition(':')
        module = modules_by_prefix[module_prefix]
        return self.navigate(module, page)

    def show_entries(self, entries):
        '''show_entries( [Entry] ) - opens a quick panel with specified entries'''
        items = map(lambda x: x.as_list(), entries) # Fun fact: map(Entry.as_list won't work after reload())

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



class Cache(object):

    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        (module, page) = key
        return self.data[module.prefix, page]

    def __setitem__(self, key, items):
        (module, page) = key
        self.data[module.prefix, page] = items


if 'data_cache' not in locals():
    data_cache = Cache()


class OmnidocClearCacheCommand(sublime_plugin.ApplicationCommand):

    def run(self, *what, **ever):
        global data_cache
        data_cache = Cache()