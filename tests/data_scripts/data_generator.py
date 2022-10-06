from collections import defaultdict
import random
import numpy as np
import pandas as pd
from typing import TypedDict


# This generates the dfs for test files to mock file validations and uploads
# Structure of test dfs - editable by different fixtures to test different cases
    # Species list: file
    # Sample Annotations Global:
    #   - PO: file
    # Gene Annotations Global:
    #   - Mapman: file
    #   - Interpro: file
    # taxid:
    # - tpm matrix: file
    # - sample annotations:
    #   - PO assignments: file
    # - gene annotations:
    #   - Mapman assignments: file
    #   - Interpro assignments: file


DfOptionalType = pd.DataFrame | None


class SpeciesSpecificDfsType(TypedDict):
    tpm_matrix: DfOptionalType
    sa_assignments: dict[str, pd.DataFrame]
    ga_assignments: dict[str, pd.DataFrame]


class DataDfType(TypedDict):
    # One global species_list
    species_list_df: DfOptionalType
    # Sample/gene annotations are collected globally
    # Each file for each type of sample/gene annotation
    sample_annotation_dfs: dict[str, pd.DataFrame]
    gene_annotation_dfs: dict[str, pd.DataFrame]
    # Dict of taxid -> dict of SpciesSpecificDfsType
    species_specific_dfs: dict[int, SpeciesSpecificDfsType]


def get_data_dfs() -> DataDfType:
    #
    # Initialize main data container
    #
    data_dfs: DataDfType = {
        "species_list_df": None,
        "sample_annotation_dfs": {},
        "gene_annotation_dfs": {},
        "species_specific_dfs": defaultdict(lambda: defaultdict(dict)),
    }

    #
    # Species file
    #
    data_dfs["species_list_df"] = pd.DataFrame([
        {
            "taxid": 9001,
            "name": "First species",
            "alias": "Lead species, Best species, King",
            "cds_source": "DAD",
            "cds_url": "https://dad.com/first_species",
            "qc_stat_log_processed": None,
            "qc_stat_p_pseudoaligned": None,
        },
        {
            "taxid": 9002,
            "name": "Second species",
            "alias": "Runner up",
            "cds_source": "MUM",
            "cds_url": "https://mum.com/second_species",
            "qc_stat_log_processed": None,
            "qc_stat_p_pseudoaligned": None,
        },
        {
            "taxid": 9003,
            "name": "Third species",
            "alias": "",
            "cds_source": "DAD",
            "cds_url": "https://dad.com/third_species",
            "qc_stat_log_processed": None,
            "qc_stat_p_pseudoaligned": None,
        },
        {
            "taxid": 9004,
            "name": "Fourth species",
            "alias": "",
            "cds_source": "MUM",
            "cds_url": "https://mum.com/fourth_species",
            "qc_stat_log_processed": None,
            "qc_stat_p_pseudoaligned": None,
        },
    ])

    #
    # Sample annotations (global)
    #   - PO
    #
    sa_type = "PO"
    data_dfs["sample_annotation_dfs"][sa_type] = pd.DataFrame(
        data={
            "label": [f"{sa_type}_{4000 + i}" for i in range(1, 100)],
            "name": [f"name_of_{sa_type}_{4000 + i}" for i in range(1, 100)],
            # The remaining fields will be specific to the sa_type
        },
    )

    #
    # Gene annotations (global)
    #   - Mapman
    #   - Interpro
    #
    ga_type = "MAPMAN"
    data_dfs["gene_annotation_dfs"][ga_type] = pd.DataFrame(
        data={
            "label": [f"{ga_type}_{7000 + i}" for i in range(1, 100)],
            "name": [f"name_of_{ga_type}_{7000 + i}" for i in range(1, 100)],
            # The remaining fields will be specific to the ga_type
            "description": [f"description_of_{ga_type}_{7000 + i}" for i in range(1, 100)],
        },
    )

    ga_type = "INTERPRO"
    data_dfs["gene_annotation_dfs"][ga_type] = pd.DataFrame(
        data={
            "label": [f"{ga_type}_{7000 + i}" for i in range(1, 100)],
            "name": [f"name_of_{ga_type}_{7000 + i}" for i in range(1, 100)],
            # The remaining fields will be specific to the ga_type
            "go_terms": [
                ", ".join([
                    f"go_{7100 + j}_{ga_type}_{7000 + i}"
                    for j in range(1, random.randint(1, 5))
                ])
                for i in range(1, 100)
            ],
        },
    )

    #
    # Files by species
    #
    for taxid in data_dfs["species_list_df"]["taxid"]:
        #
        # TPM matrix
        #
        n_samples = np.random.randint(low=10, high=20, size=None, dtype=int)
        n_genes = np.random.randint(low=10, high=40, size=None, dtype=int)
        sample_labels = [f"sample_{5000 + i}_tax{taxid}" for i in range(1, n_samples + 1)]
        gene_labels = [f"gene_{8000 + i}_tax{taxid}" for i in range(1, n_genes + 1)]
        tpm_df = pd.DataFrame(
            data=np.random.random_sample(size=(n_genes, n_samples)) * 100,
            columns=sample_labels,
            index=gene_labels,
        )
        tpm_df = pd.concat([tpm_df.index.to_series(name="gene_labels"), tpm_df], axis=1)
        data_dfs["species_specific_dfs"][taxid]["tpm_matrix"] = tpm_df

        #
        # Sample annotation assignments
        #
        sa_type = "PO"
        possible_sa_labels = data_dfs["sample_annotation_dfs"][sa_type]["label"].sample(10).tolist()
        # Give 10/110 probability of no sample annotation for a sample
        possible_sa_labels.extend([""] * 10)
        data_dfs["species_specific_dfs"][taxid]["sa_assignments"][sa_type] = pd.DataFrame(
            data={
                # Take all labels from tpm matrix
                "sample_label": sample_labels,
                # Randomize from global and include None as possibility too
                "annotation_label": [
                    random.choice(possible_sa_labels)
                    for _ in range(len(sample_labels))
                ],
            },
        )

        #
        # Gene annotation assignments
        #
        ga_type = "MAPMAN"
        possible_ga_labels = data_dfs["gene_annotation_dfs"][ga_type]["label"].sample(10).tolist()
        # Give 5/105 probability of no gene annotation for a gene
        possible_ga_labels.extend([""] * 5)
        data_dfs["species_specific_dfs"][taxid]["ga_assignments"][ga_type] = pd.DataFrame(
            data={
                # Take all labels from tpm matrix
                "gene_label": gene_labels,
                # Randomize from global and include None as possibility too
                "annotation_label": [
                    random.choice(possible_ga_labels)
                    for _ in range(len(gene_labels))
                ],
            },
        )

        ga_type = "INTERPRO"
        possible_ga_labels = data_dfs["gene_annotation_dfs"][ga_type]["label"].sample(10).tolist()
        # Give 5/105 probability of no gene annotation for a gene
        possible_ga_labels.extend([""] * 5)
        data_dfs["species_specific_dfs"][taxid]["ga_assignments"][ga_type] = pd.DataFrame(
            data={
                # Take all labels from tpm matrix
                "gene_label": gene_labels,
                # Randomize from global and include None as possibility too
                "annotation_label": [
                    random.choice(possible_ga_labels)
                    for _ in range(len(gene_labels))
                ],
            },
        )

    return data_dfs


__all__ = ["get_data_dfs"]
