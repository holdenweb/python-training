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

* `Homebrew`:
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

* `poetry` - I recommend using the custom installer, see
  https://python-poetry.org/docs/.

* `pre-commit` - not strictly required, but strongly recommended. A `.pre-commit-config.yaml` is included.

* `MongoDB` - a server listening on port localhost.27017.
  On my Mac

  If mongodb hasn't been installed before you may need to first run:
  `brew tap mongodb/brew`

  `brew install mongodb-community@5.0`
  `brew services start mongodb-community` ensures the server starts,
  and will thereafter start up on boot.

Add credentials file to
  ~/.credentials.json

Authenticate with Google

The following commands worked for me on my Mac.
No other guarantees are offered.

    git clone git@github.com:holdenweb/python-training.git
    cd python-training
    poetry env use 3.9      # Includes support for 3.7 through 3.10    
    poetry install

    # Before continuing, set up your environment to have the
    # `src\transformers` directory in your path (PYTHONPATH=...)
    # Ensure you are in the root of the python-training project and run:
    export PYTHONPATH=$(pwd)/src/transformers

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
