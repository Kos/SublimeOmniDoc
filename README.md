# OmniDoc

General documentation plug-in for Sublime Text 2

## What's this?

Think of it as...

- A **code completion** engine (or a substitute for one) for libraries. Half-automated: ask for "class XYZ" or "function Foo", get a list of members or parameters. This works well with dynamic languages, where automated tools often can't infer the type (but you usually know it).
- A quick access tool for **all kinds of documentation**. Navigate lists of items. When in doubt, have a browser tab opened on documentation.
- A platform for you to extend and use. Plug in any kinds or reference material that you often use - not limited to programming.
- A productivity helper that saves you much alt-tabbing to look things up.

## How to use?

See the OmniDoc commands in the command palette.

The `module list` command is a good starting point. Explore the members easily using Sublime's fuzzy matching. Documentation is organised into "modules". Each module corresponds to a source of documentation and is identified by a short name ("prefix"). Each module has an "index page" and a number of named pages (for example, one page for a function or a class).

Pages consist of entries and are displayed using Sublime's quick panel. Some entries (such as these in module index) work as links to other pages, while others just insert stuff (like a method signature) into the editor.

The `show documentation` command is what you'll be spending the most time with: Type something like `gl:vertex`, run this command and you'll obtain all pages from module `gl` that have `vertex` in their name. Alternatively, `gl:` will show you the module's index.

I recommend to create a key binding for this command. Example key binding to paste into `Preferences` -> `Key Bindings - User`:

	{ "keys": ["ctrl+shift+o"], "command": "omnidoc" }

## What documentation is supported out of the box?

- [OpenGL](http://www.opengl.org/sdk/docs/man/xhtml/) (man pages)
- [Qt](http://qt-project.org/doc/qt-4.8/)
- [SQLAlchemy](http://docs.sqlalchemy.org/en/rel_0_8/) (a tidbit)

## Can it also support XYZ?

Yes! Adding data sources is easy (if you know Python and HTML) and a matter of writing like 50 lines of code. Use existing connectors as examples.

Go ahead and contribute back your connectors if you feel they're going to be useful for someone.

## How to install?

Clone this repository into your `Packages`.

I'll submit the project into package control when I hit a couple todos more.