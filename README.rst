Python DSL / Python Sandbox
===========================

The real objective of this work is to provide an easy way to use python as a
DSL, so that you can save in the DB little scripts of programable logic.

Sandboxing rant
---------------

I have been a while wondering why everyone complains about python sandboxing
being broken, and I don't really understand.

This can be a PoC about how to make python sandboxing great again. The idea
is quite straightforward, the more features you want to let people have, the
more you need to invest on permissions.

This poc uses the Cerberus as validation backend, a homemade ast to dict
conversor, and a all those dangerous eval() functions.

The idea is simple, instead of trying to cut down the script on execution
time, we just validate the script's AST, and if it doesn't use anything
forbidden, we run it in a controlled namespace.

The simple script example is what I need for the python DSL. For example,
import statements are not permitted by default.
