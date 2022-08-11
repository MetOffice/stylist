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
          [-configuration FILENAME]
          [-style NAME]
          FILE ...`

The only required arguments are a configuration file and one or more
filenames. These are the files which will be checked. If a directory is
specified then the tool will automatically descend into it checking all files
which it recognises by extension.

If you want a running commentary of what the tool is doing then use the
`-verbose` argument.

A configuration file may specified with `-configuration` . This file should be
formatted as documented below. There must be a configuration file which defines
at least one style. While the fallback mechanism which allows for user and site
configurations has not been implemented it must be specified with this argument.

The configuration may define several styles, in which case one can be chosen
using the `-style` argument. If it is not then the first in the configuration
file will be used.

### Configuration File

The configuration file is a python script.

The processing pipelines for different file types are specified with
`FilePipe` objects. The variable to which it is assigned names the
file name extension it refers to. The first argument is the language source
type while subsequent arguments are text preprocessing stages.

```
from stylist.source import (FilePipe,
                            FortranSource,
                            PFUnitProcessor,
                            FortranPreprocessor)

pf = FilePipe(FortranSource, PFUnitProcessor, FortranPreprocessor)
```

Meanwhile styles are defined in a similar way. The variable name is the style
name and the object is constructed with the rules of which it consists.

```
from re import compile as recompile
from stylist.style import Style
from stylist.fortran import FortranCharacterset, KindPattern

simple = Style(FortranCharactersest(),
               KindPattern(integer=recompile(r'i_.+'),
                           real=recompile(r'r_.+'))
```
