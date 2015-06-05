HitchTest
=========

HitchTest is a part of the hitch testing framework which compiles
YAML and jinja2 to python unittest.

Why?
====

* Individual test cases should be declarative.
* The engine that runs them should be imperative.

YAML provides an easy way to provide a *less* powerful language to
write test scenarios in that can be easily compiled to a more powerful
language (python). This makes reading, writing, parsing and adding
features to test cases much easier.

Theoretically, the YAML should be readable and writable by non-programmers.
