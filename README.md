![](https://github.com/MetOffice/stylist/workflows/Python%20package/badge.svg)

# Stylist

Stylist is a code style checking tool built on a framework which supports
multiple styles across multiple languages.

But aren't there many code style checking tools out there, why create a new
one?

The simple reason is that few of them support Fortran, a language still in
widespread use in the scientific computing domain. They can also tend towards
the zealous when enforcing the "one true style" whereas long running science
models tend to diverge quite radically in what they like, style-wise.

Large models also tend to be implemented using more than one language so a
tool which is capable of understanding all of them would be welcomed by
science developers.

Thus a tool was developed based on a framework which hopes to support ready
extension and reconfiguration.

The project is still in its infancy so only a few rules have been implemented
and only for Fortran. Stubs are provided to show how it might be extended to
support C.

Find the project at https://github.com/MetOffice/stylist

## Installation

Installation can be as simple as `pip install stylist` or
`conda install -c conda-forge stylist`.

As always it is also possible to install from the project source by running
`python setup.py`. The source may be obtained by downloading a tarball or by
cloning the repository.

## Usage

Stylist provides a command-line tool `stylist` for normal use. It can also be
used as a package if you want to integrate it with another tool. Documentation
regarding this second option is maintained in the project wiki.

### On the Command Line

The command-line tool is not complicated to use:

 `stylist [-help] [-verbose]
          [-map-extension EXTENSION:LANGUAGE[:PREPROCESSOR:...]]
          FILE ...`

The only required arguments are one or more filenames. These are the files
which will be checked. If a directory is specified then the tool will
automatically descend into it checking all files which it recognises by
extension.

If you wish to make the tool aware of new extensions then use the
`-map-extension` argument. It takes a colon separated list. The first item
is the plain extension (no preceding full-stop). After that comes the
language to understand the file as. Finally a list of zero or more
preprocessors to apply to the file before parsing.

For example: `stylist -map-extension spesh:fortran:fpp:pfp`

The keys for selecting language and preprocessor are found in `__main__.py`.

If you want a running commentary of what the tool is doing then use the
`-verbose` argument.
