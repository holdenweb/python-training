# The Transformer Project

Utilities to ingest data in one form and present it in others.

The first example saves Google sheets data as MongoDB records,
using mongoengine (which Django ORM users will find familiar).

A baseline for expansion and enhancement by those
interested in using the project as a testbed for ideas
and techniques.

While not a complicated project,
it encourages discussion about
architectural as well as coding matters.

## Getting Started

You will need thge following dependencies installed:

* A recent (3.7+) Python installation (currently developed on 3.9)

* `poetry` - I recommend using the custom installer, see
  https://python-poetry.org/docs/.

* `pre-commit` - not strictly required, but strongly recommended. A `.pre-commit-config.yaml` is included.

* `MongoDB` - a server listening on port localhost.27017.
  On my Mac
  `brew install mongodb-community mongodb-database-tools mongosh` did the trick.
  `brew services start mongodb-community` ensures the server starts,
  and will thereafter start up on boot.


The following commands worked for me on my Mac.
No other guarantees are offered.

    git clone git@github.com:holdenweb/sheetpub.git
    cd sheetpub
    poetry env use 3.9      # Includes support for 3.7 through 3.10
    # Before continuinng, set up your environment (PYTHONPATH= ...)
    # Ensure that the `src\transformers` directory is on there!
    make test
    make pull               # You need read permission on the
    make pull               # spreadsheet - second run verifies

If you've got this far without issues, the Alpha is ready to go.
But you didn't, did you? :-)

Just supposing you did, you might also be interested in trying

    poetry run python src/transformers/document.py

But at present you'll have to figure out the user interface
by reading the code.
Sorry!
