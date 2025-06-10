# Setting up and managing the repository

## For the first time

Clone the repository to your local machine.

    git clone git@github.com:wirriamm/omnibus-uploader-2.git

Setup the local Python virtual environment, using Python >=3.10 . You may use other virutal environment other than venv.

    python -m venv venv
    source venv/bin/activate

Install Python dependencies.

    pip install --upgrade pip
    pip install -r requirements.txt

For subsequent runs, these steps do not need to be repeated anymore.

## Configurations

Create the `.env` file to store environment variables. This file is not checked into version control as it may contain secrets. However, a template `.env.example` is provided and checked into version control, which can be used to create the `.env` file.

    cp .env.example .env

Then open `.env` file and update the variables.

- DATA_DIR: This is the directory in which the processed files are stored and parsed for uploading.
- DATABASE_URL: The database connection url. "mongodb://localhost:27017" for local database instance. For production, go to Atlas to retrieve the URL.
- DATABASE_NAME: A unique string to name the database, in a single word without whitespace



## For each run

Activate the virutal environment. This step has to be done everytime you begin work with the repository in a new shell.

    source venv/bin/activate

You are now ready to run the code scripts.


## For contributing changes to the repository

Before making any changes, checkout a new branch. This section is **not** needed if you just need to run the scripts and not store any changes to the code to the remote repository on Github.

    git co -b feat/<new-feature-name>

Then, make your changes in the new branch and commit your changes to the source code.

    git add .
    git commit -m "feat: <describe your feature>"
    git status

Once you are done commiting your changes, push to the remote repository on Github

    git push origin feat/<new-feature-name>

Then, go to Github [https://github.com/wirriamm/omnibus-uploader-2/pulls](https://github.com/wirriamm/omnibus-uploader-2/pulls){:target="_blank"}. Open a new pull request (PR) for merging your changes to the main branch. Describe the changes in the PR. Wait for code owner to approve your changes and merge it to the main branch.

Once the PR has been merged to main branch, you have to update your local main branch by pulling from the remote (Github) main branch.

    git co main
    git pull origin main
