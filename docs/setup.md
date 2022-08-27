# Setting up

## For the first time

Clone the repository to your local machine.

    git clone git@github.com:wirriamm/omnibus-uploader-2.git

Setup the local Python virtual environment, using Python >=3.10 . You may use other virutal environment other than venv.

    python -m venv venv

Install Python dependencies.

    pip install --upgrade pip
    pip install -r requirements.txt

## For each run

Activate the virutal environment. This step has to be done everytime you begin work with the repository in a new shell.

    source venv/bin/activate
