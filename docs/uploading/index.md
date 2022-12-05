# Design of the uploader

The uploader is designed as a set of object-oriented utilities that is modular and therefore hopefully decoupled and more easily configurable. The main parts of the uploader includes:


| Component | Description |
| - | - |
| Models | Model classes that inherits from Pydantic's base class, to define the data shape and validations |
| Parsers | Parser classes that parses files and shape them via models |
| Controllers | Controller classes wraps uploading logic for certain parts of the data, glueing together the parsers, models and utility functions to upload to the database. |



Utility functions

| Directory | Description |
| - | - |
| /uploader/db_setup/ | Functions to setup DB, get DB driver instance, get DB collection, setup DB indexes (if does not exists yet), based on the DATABASE_URL AND DATABASE_NAME defined in the `.env` file. |
| /uploader/db_queries/ | Functions to read or write to the DB |


Integration tests are written and run using pytest. Tests are all in the `/tests` directory and can be run with pytest.

Data filepaths are defined in `config/filepath_definitions.py` and can be configured.


## Models


!!! warning "Work in Progress"

    :construction_worker_tone1: _To be updated_


## Parsers


!!! warning "Work in Progress"

    :construction_worker_tone1: _To be updated_


## Controllers


!!! warning "Work in Progress"

    :construction_worker_tone1: _To be updated_
