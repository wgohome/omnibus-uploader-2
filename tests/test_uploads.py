from config.filepath_definitions import test_filepath_definitions as filepath_definitions
from uploader.controllers import (
    SpeciesController,
    GeneController,
    GeneAnnotationController,
    GeneAnnotationBucketController,
    SampleAnnotationController,
    CoexpressionController,
)
from uploader.models import (
    GeneAnnotationType,
    SampleAnnotationType,
)
from uploader.parsers import (
    SpeciesParser,
    GeneParser,
    MapmanUnitParser,
    InterproUnitParser,
    GeneAnnotationAssignmentParser,
    SampleAnnotationAssignmentParser,
    TpmParser,
)


def test_upload_species(write_file_base, test_db):
    species_controller = SpeciesController(db=test_db)
    species_parser = SpeciesParser(
        filepath=filepath_definitions.get_species_list_filepath()
    )
    species_controller.upload_many(species_parser.parse())
    species_id_map = species_controller.get_taxid_id_map()
    assert len(species_id_map) > 0
    assert len([*species_parser.parse()]) == len(species_id_map)


def test_upload_genes(write_file_base, test_db):
    species_controller = SpeciesController(db=test_db)
    species_parser = SpeciesParser(
        filepath=filepath_definitions.get_species_list_filepath()
    )
    species_controller.upload_many(species_parser.parse())
    species_id_map = species_controller.get_taxid_id_map()
    for taxid, species_id in species_id_map.items():
        gene_controller = GeneController(taxid=taxid, species_id=species_id, db=test_db)
        gene_parser = GeneParser(
            filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
            species_id=species_id
        )
        gene_controller.upload_many(gene_parser.parse())
        label_id_map = gene_controller.get_label_id_map()
        assert len(label_id_map) > 0
        assert len([*gene_parser.parse()]) == len(label_id_map)

        # Upload pcc too
        coexpression_controller = CoexpressionController(
            taxid=taxid,
            species_id=species_id,
            gene_id_map=label_id_map,
            n_neighbors=5,
            # Needed to override files dir for test
            custom_filepath_definitions=filepath_definitions,
        )
        while True:
            row = coexpression_controller.get_next_row()
            if row is None:
                break
            print(f"Processing gene {row.gene_label}")
            gene_controller.set_coexpressed_genes(
                gene_id=label_id_map[row.gene_label],
                neighbors=row.neighbors,
            )


def test_upload_mapman_units(write_file_base, test_db):
    mapman_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.MAPMAN, db=test_db)
    mapman_unit_parser = MapmanUnitParser(
        filepath=filepath_definitions.get_ga_filepath(ga_type=GeneAnnotationType.MAPMAN)
    )
    mapman_ga_controller.upload_many(mapman_unit_parser.parse())
    mapman_id_map = mapman_ga_controller.get_label_id_map()
    assert len(mapman_id_map) > 0
    assert len([*mapman_unit_parser.parse()]) == len(mapman_id_map)


def test_upload_interpro_units(write_file_base, test_db):
    interpro_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.INTERPRO, db=test_db)
    interpro_unit_parser = InterproUnitParser(
        filepath=filepath_definitions.get_ga_filepath(ga_type=GeneAnnotationType.INTERPRO)
    )
    interpro_ga_controller.upload_many(interpro_unit_parser.parse())
    interpro_id_map = interpro_ga_controller.get_label_id_map()
    assert len(interpro_id_map) > 0
    assert len([*interpro_unit_parser.parse()]) == len(interpro_id_map)


def test_upload_mapman_buckets(write_file_base, test_db):
    species_controller = SpeciesController(db=test_db)
    species_parser = SpeciesParser(
        filepath=filepath_definitions.get_species_list_filepath()
    )
    species_controller.upload_many(species_parser.parse())
    species_id_map = species_controller.get_taxid_id_map()

    mapman_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.MAPMAN, db=test_db)
    mapman_unit_parser = MapmanUnitParser(
        filepath=filepath_definitions.get_ga_filepath(ga_type=GeneAnnotationType.MAPMAN)
    )
    mapman_ga_controller.upload_many(mapman_unit_parser.parse())
    mapman_id_map = mapman_ga_controller.get_label_id_map()

    for taxid, species_id in species_id_map.items():
        gene_controller = GeneController(taxid=taxid, species_id=species_id, db=test_db)
        gene_parser = GeneParser(
            filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
            species_id=species_id
        )
        gene_controller.upload_many(gene_parser.parse())
        label_id_map = gene_controller.get_label_id_map()

        mapman_ga_bucket_controller = GeneAnnotationBucketController(
            species_id=species_id,
            ga_type=GeneAnnotationType.MAPMAN,
            ga_id_map=mapman_id_map,
            gene_id_map=gene_controller.get_label_id_map(),
            db=test_db
        )
        ga_assignment_parser = GeneAnnotationAssignmentParser(
            filepath=filepath_definitions.get_ga_assignment_filepath(
                ga_type=GeneAnnotationType.MAPMAN,
                taxid=taxid
            )
        )
        mapman_ga_bucket_controller.append_all_rows_to_buckets(
            rows=ga_assignment_parser.parse()
        )
        mapman_ga_bucket_controller.upload_many_from_buckets()


def test_upload_interpro_buckets(write_file_base, test_db):
    species_controller = SpeciesController(db=test_db)
    species_parser = SpeciesParser(
        filepath=filepath_definitions.get_species_list_filepath()
    )
    species_controller.upload_many(species_parser.parse())
    species_id_map = species_controller.get_taxid_id_map()

    interpro_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.INTERPRO, db=test_db)
    interpro_unit_parser = InterproUnitParser(
        filepath=filepath_definitions.get_ga_filepath(ga_type=GeneAnnotationType.INTERPRO)
    )
    interpro_ga_controller.upload_many(interpro_unit_parser.parse())
    interpro_id_map = interpro_ga_controller.get_label_id_map()

    for taxid, species_id in species_id_map.items():
        gene_controller = GeneController(taxid=taxid, species_id=species_id, db=test_db)
        gene_parser = GeneParser(
            filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
            species_id=species_id
        )
        gene_controller.upload_many(gene_parser.parse())
        label_id_map = gene_controller.get_label_id_map()

        interpro_ga_bucket_controller = GeneAnnotationBucketController(
            species_id=species_id,
            ga_type=GeneAnnotationType.INTERPRO,
            ga_id_map=interpro_id_map,
            gene_id_map=gene_controller.get_label_id_map(),
            db=test_db
        )
        ga_assignment_parser = GeneAnnotationAssignmentParser(
            filepath=filepath_definitions.get_ga_assignment_filepath(
                ga_type=GeneAnnotationType.INTERPRO,
                taxid=taxid
            )
        )
        interpro_ga_bucket_controller.append_all_rows_to_buckets(
            rows=ga_assignment_parser.parse()
        )
        interpro_ga_bucket_controller.upload_many_from_buckets()


def test_upload_sample_annotation_docs(write_file_base, test_db):
    species_controller = SpeciesController(db=test_db)
    species_parser = SpeciesParser(
        filepath=filepath_definitions.get_species_list_filepath()
    )
    species_controller.upload_many(species_parser.parse())
    species_id_map = species_controller.get_taxid_id_map()

    for taxid, species_id in species_id_map.items():
        gene_controller = GeneController(taxid=taxid, species_id=species_id, db=test_db)
        gene_parser = GeneParser(
            filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
            species_id=species_id
        )
        gene_controller.upload_many(gene_parser.parse())
        label_id_map = gene_controller.get_label_id_map()

        print(f"Uploading TPM values bucketed by sample annotations for taxid{taxid}")
        # Get header of samples
        # Get row by row of tpms
        tpm_parser = TpmParser(
            filepath=filepath_definitions.get_tpm_filepath(taxid=taxid)
        )
        # Get sample -> po label mapping
        sa_assignment_parser = SampleAnnotationAssignmentParser(
            filepath=filepath_definitions.get_sa_assignment_filepath(sa_type=SampleAnnotationType.PO.value, taxid=taxid)
        )
        po_controller = SampleAnnotationController(
            species_id=species_id,
            gene_id_map=gene_controller.get_label_id_map(),
            sa_type=SampleAnnotationType.PO,
            sample_labels=tpm_parser.get_sample_labels(),
            sa_assignments=sa_assignment_parser.get_sample_annotation_map(),
        )
        po_controller.upload_many(row_iterator=tpm_parser.parse())
