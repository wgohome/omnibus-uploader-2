# Protein sequence search

To enable users to identify their gene of interest through a protein sequence, a protein search tool is required. The tool should then be deplyed and provisioned to the user-facing application.


## Choice of sequence search tool: Diamond

[Diamond]() was chosen as the protein search tool to identify genes from given protein sequences, because of its speed 💨, low memory footprint 🐾 and comparable accuracy 🎯. Speed is essential in a user facing application, while laser accuracy makes less of a difference to user experience since the user will be choosing from the recommended search result anyway.


## Data processing

Protein sequences from processed PEP files [earlier](/data-processing/protein_sequences/#data-availability){:target="_blank"}. Note that one species (GOSAR, taxid 29729) does not have an available PEP file and is hence not searchable by protein sequence.

The PEP files were used to build a diamond database, which is the reference target used when searching for an unknown protein sequence.


## Service availability

The service is an API written in FastAPI, source code available on [Github](https://github.com/wirriamm/diamond-search){:target="_blank"}, hosted on Google Cloud Platform.

The interactive Open API docs (live in production) can be found [here](https://diamond-search-z4ugr225pa-uc.a.run.app){:target="_blank"}.
