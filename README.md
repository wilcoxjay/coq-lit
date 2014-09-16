coq-lit.py: Literate Coq Blogging 
==================================

This python script processes special commands inside comments in Coq
source files to produce markdown and raw html that generates a blog
post. An example may be found
[here](http://homes.cs.washington.edu/~jrw12/dep-destruct.html)
([source](http://homes.cs.washington.edu/~jrw12/dep-destruct.v)).

Dependencies
-------------

You'll need:
* python 3.x
* jQuery (tested with 2.1.1)
* jQuery UI (tested with 1.11.1)

Commands
----------

**Note: All commands must appear at the very beginning of a line. This
  includes comment-closing characters.**

* `(**` begins a blog output comment, ended by `*)`

* `(*begin code*)` begins a block of Coq code to be pretty printed to
  the blog, ended by `(*end code*)`. Coq code not appearing between
  such commands will not be printed. (This can be useful for glossing
  over things such as `Undo` and `Abort`.)

* `(*context` begins a tooltip (popup) proof context block, ended by
  `*)`. This captures the line of code following the `*)` and makes it
  pop up the given context on hover.

