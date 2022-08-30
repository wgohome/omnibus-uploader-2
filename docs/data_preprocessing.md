# Data sources and preprocessing

## TPM matrices

!!! warning "Work in Progress"

    :construction_worker_tone1: _To be updated_


## Protein sequence annotations

### Sources used

For each species, the PEP files (of the matching version as the CDS used for transcript pseudoalignment) were obtained. They were used in two ways.

1. The PEP files were passed through Interproscan to annotate the ==**PFAM identifiers**== and ==**GO terms**== associated with each gene.

2. The PEP files are as the protein sequence database for sequence based search using the [bbuchfink/diamond](https://github.com/bbuchfink/diamond) aligner.

To ensure that the gene identifiers remain consistent, we preprocess the gene identifiers to match those in the CDS files (and therefore in the TPM files). We chose the CDS identifiers as the standard as they tend to be cleaner, and because there are more gene identifiers in the CDS than in the PEP files, presumably because not all genes in the CDS have known protein products.

### Matching gene identifiers

These heuristics were used for preprocessing the gene identifiers.

- Check if identifiers in TPM matrix/CDS matches or is a subset of PEP's. If yes, then the identifier in PEP file is replaced.

- If TPM's identifier don't match any in PEP, then
    - The gene shall have no matching gene annotation for PFAM
    - The gene will not be searchable by protein sequence

- If PEP's identifier don't match any in TPM, then
    - The gene entry can be removed/ignored from the PEP file
