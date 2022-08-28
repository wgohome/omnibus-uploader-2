# Overview

This tool serves as the interface for writing data to the Mongo DB instance, which is read by the front-end application [Plant Gene Expression Omnibus](#). This is meant to be used by the administrators of this database (1).
{.annotate}

1. Hello

Lorem ipsum dolor sit amet, (2) consectetur adipiscing elit.
{ .annotate }
2.  :man_raising_hand: I'm an annotation! I can contain `code`, __formatted
    text__, images, ... basically anything that can be expressed in Markdown.


???+ info "Source code"

    :octicons-desktop-download-16:  For source code of the uploader, visit [this Github repo](https://github.com/wirriamm/omnibus-uploader-2). Go to [setup](setup.md) for how to run the code locally.

    :nail_care_tone1: Looking for the source code of the front-end application? Visit [this Github repo](https://github.com/wirriamm/plant-omnibus) instead.


## Components of the tool

!!! warning "Work in Progress"

    :construction_worker_tone1: _To be updated_


## Input files

Input file format that is currently supported is csv, as is the customary output format from upstream bioinformatics tools used in the Mutwil Lab. The file entities that needs to be prepared before the upload are the following:

| File | Required fields | Remarks |
| :--- | :--- | :--- |
| Species list | <ul><li>Tax ID</li><li>Scientific name</li><li>CDS Source</li></ul> | Only one file for all species |
| TPM matrices | <ul><li>Gene ID (row label)</li><li>Sample Accession (col label)</li><li>TPM values (body)</li></ul>| One per species |
| Plant Ontology annotations | <ul><li></li><li></li><li></li></ul> | One per species |
| Interpro gene annotations | <ul><li></li><li></li><li></li></ul> | One per species |
| Mapman gene annotations | <ul><li></li><li></li><li></li></ul> | One per species |

## Steps

The scope of the tool includes:

- Checks tsv files for validity before begining uploading process
    - The files for each species are present
    - Data format in every file is parsable by our readers
    - Gene identifiers from TPM matrix are the default ones. The gene identifiers in other files should match those in the TPM matrix.
    - Sample accession in TPM matrix are the default ones. Check that those in the Plant Ontology annotation files are matching. Warn about species without any annotated samples.

- Parse tsv files for upload
    - Parse using generators, with help shaping data using Pydantic
    - Directly upload documents to Mongo DB via pymongo connection
    - Report upload status in a log
