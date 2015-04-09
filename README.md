utils
=====

`utils` is a repository of scripts used by the [Open Computing Facility][ocf]
at the University of California, Berkeley.

## What belongs here
### Scripts for humans do

In general, scripts which might be executed by a person should go here.
System scripts (things that go primarily in cronjobs or similar) should go in
the [ocf/puppet][ocf/puppet] repo instead.

Scripts of all languages are welcome, and should be organized into appropriate
directories. Use `staff/` for anything that will typically only be executed by
staff.

### Libraries don't

If your utility is meant to be imported, it should probably go in
[ocflib][ocflib] instead. If you're writing a script whose functionality might
be useful elsewhere, separate that out, put it in ocflib, and call it from a
binary in this repo.

## General best practices
### All languages

* Executable files should be marked executable, contain a proper shebang, and
  generally not have a file extension.

### Python

* Use [ocflib][ocflib] functionality when it exists, and put reusable code
  there (and call it from an executable here).
* When possible, target Python 3.2 and 3.4 (same versions as ocflib)
* Generally follow [PEP8][pep8].

### Shell/Bash

* [Use `/bin/bash` over `/bin/sh`][use-bin-bash] unless your script is for some
  alien environment where there is no bash. Don't be afraid to use bashisms.
* Typically add `-e` to the end of the shebang (or `set -e`) to stop on errors.
* Quote things and otherwise follow best practices.

### Other languages

* Consider writing in Python instead.

[ocf]: https://www.ocf.berkeley.edu/
[ocf/puppet]: https://github.com/ocf/puppet/
[ocflib]: https://github.com/ocf/ocflib/
[use-bin-bash]: https://google-styleguide.googlecode.com/svn/trunk/shell.xml?showone=Which_Shell_to_Use#Which_Shell_to_Use
[pep8]: https://www.python.org/dev/peps/pep-0008/
