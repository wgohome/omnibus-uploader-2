# Uploader for Plant Gene Expression Omnibus

This is an admin tooling for uploading gene expression data and annotations directly to the MongoDB database instance.

## Repository Setup

Create a `.env` file specifying these secret variables

- `DATABASE_URL` (with the relevant MongoDB username and password if required)
- `DATA_DIR` (where the source of data to be uploaded comes from)
- `LOG_DIR` (where logs should be dumped to)

Create a virtual environment to use Python >= 3.10.2

```
python -m venv venv
```

Install dependencies via

```
source venv/bin/activate
pip install -r requirements.txt
```
