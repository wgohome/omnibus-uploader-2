from config.filepath_definitions import filepath_definitions
from uploader.controllers import (
    SpeciesController,
    GeneController,
    GeneAnnotationController,
    GeneAnnotationBucketController,
    SampleAnnotationController,
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


#
# Upload species
#


print("Processing species file")
species_controller = SpeciesController()
species_parser = SpeciesParser(
    filepath=filepath_definitions.get_species_list_filepath()
)
species_controller.upload_many(species_parser.parse())
species_id_map = species_controller.get_taxid_id_map()
new_species_id_map = {k: v for k, v in species_id_map.items() if k in [85692, 4182, 4236]}


#
# Upload Gene Annotations
#


print("Processing MAPMAN annotations")
mapman_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.MAPMAN)
mapman_unit_parser = MapmanUnitParser(
    filepath=filepath_definitions.get_ga_filepath(ga_type=GeneAnnotationType.MAPMAN)
)
mapman_ga_controller.upload_many(mapman_unit_parser.parse())
mapman_id_map = mapman_ga_controller.get_label_id_map()


print("Processing INTERPRO annotations")
interpro_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.INTERPRO)
interpro_unit_parser = InterproUnitParser(
    filepath=filepath_definitions.get_ga_filepath(ga_type=GeneAnnotationType.INTERPRO)
)
interpro_ga_controller.upload_many(interpro_unit_parser.parse())
interpro_id_map = interpro_ga_controller.get_label_id_map()


#
# Upload genes per species
#


for taxid, species_id in new_species_id_map.items():
    print(f"Uploading genes for taxid{taxid}")
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    gene_parser = GeneParser(
        filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
        species_id=species_id
    )
    gene_controller.upload_many(gene_parser.parse())
    label_id_map = gene_controller.get_label_id_map()


#
# Upload TPM values with sample annotations
#


for taxid, species_id in new_species_id_map.items():
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
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


#
# Upload Gene Annotation Buckets
#


for taxid, species_id in new_species_id_map.items():
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    #
    # MAPMAN
    #
    mapman_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.MAPMAN)
    mapman_id_map = mapman_ga_controller.get_label_id_map()

    print(f"Uploading MAPMAN assignments for taxid{taxid}")
    mapman_ga_bucket_controller = GeneAnnotationBucketController(
        taxid=taxid,
        ga_type=GeneAnnotationType.MAPMAN,
        ga_id_map=mapman_id_map,
        gene_id_map=gene_controller.get_label_id_map()
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
    gene_controller.append_ga_ids(
        gene_to_ga_map = mapman_ga_bucket_controller.get_gene_ga_refs()
    )

    #
    # INTERPRO
    #
    interpro_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.INTERPRO)
    interpro_id_map = interpro_ga_controller.get_label_id_map()

    print(f"Uploading INTERPRO assignments for taxid{taxid}")
    interpro_ga_bucket_controller = GeneAnnotationBucketController(
        taxid=taxid,
        ga_type=GeneAnnotationType.INTERPRO,
        ga_id_map=interpro_id_map,
        gene_id_map=gene_controller.get_label_id_map(),
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
    gene_controller.append_ga_ids(
        gene_to_ga_map = interpro_ga_bucket_controller.get_gene_ga_refs()
    )
