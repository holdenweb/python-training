# The Transformer Project

Utilities to ingest data in one form and present it in others.

The first example saves Google sheets data as MongoDB records,
using mongoengine (which Django ORM users will find familiar).

Plus a bit more Python to do some simple reporting.

A baseline for expansion and enhancement by DIT staff
interested in using the project as a testbed for ideas
and techniques.

## Getting Started

You will need to following dependencies installed:

* A recent (3.6+?) Python installation (currently only tested on 3.9)

* `poetry` - I recommend using the custom installer, see
  https://python-poetry.org/docs/

* `pre-commit` - not strictly required, but strongly recommended.

* `MongoDB` - a server listening on port localhost.27017

The following commands worked for me on my Mac. No other
guarantees are offered.

    git clone git@github.com:holdenweb/sheetpub.git
    cd sheetpub
    poetry env use 3.9      # Want to support 3.7 through 3.10
    source .env             # Set up your environment
    make test
    make pull               # You need read permission on the
    make pull               # spreadsheet - second run verifies
    make reports            # A few little sample reports

Note that the Python environment
created by poetry
is far heavier than it needs to be.
It has supported various other undocumented experiments.
Feel free to refactor mercilessly.
