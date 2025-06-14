from config.filepath_definitions import filepath_definitions
from uploader.controllers import (
    SpeciesController,
    GeneController,
    GeneAnnotationController,
    GeneAnnotationBucketController,
    SampleAnnotationController,
    SampleAnnotationSpmUpdater, # TO DELETE
    CoexpressionController,
    SampleAnnotationEntityController,
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
    PoUnitParser,
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

# curr_species_id_map = {
#     k: v for k, v in species_id_map.items()
#     if k in [29729, 3726, 59689, 3888, 37334, 3562, 28526, 90675, 4111, 3641, 63459, 74649, 29655, 37682, 4432, 3625, 57918, 4155, 180498, 4572, 3649, 29730, 49451, 3821, 62335, 4529, 51953, 296587, 4543, 4686, 50452, 93759, 28532, 210143, 49390, 110835, 71139, 85681, 81985, 157791, 57577, 3988, 3914, 4182, 4236, 85692]
# }
curr_species_id_map = species_id_map


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


for taxid, species_id in curr_species_id_map.items():
    print(f"Uploading genes for taxid{taxid}")
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    gene_parser = GeneParser(
        filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
        species_id=species_id
    )
    gene_controller.upload_many(gene_parser.parse())
    gene_label_id_map = gene_controller.get_label_id_map()


#
# Upload top 50 coexpressed gene neighbours
#


for taxid, species_id in curr_species_id_map.items():
    print(f"Uploading coexpressed genes for taxid{taxid}")
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    gene_label_id_map = gene_controller.get_label_id_map()

    coexpression_controller = CoexpressionController(
        taxid=taxid,
        species_id=species_id,
        gene_id_map=gene_label_id_map,
    )
    while True:
        row = coexpression_controller.get_next_row()
        if row is None:
            break
        gene_controller.set_coexpressed_genes(
            gene_id=gene_label_id_map[row.gene_label],
            neighbors=row.neighbors,
        )


#
# Initialize sample annotation entities
#

po_parser = PoUnitParser(
    filepath=filepath_definitions.get_sa_filepath(sa_type="PO")
)
po_entity_controller = SampleAnnotationEntityController(
    new_sa_entities=po_parser.parse()
)


#
# Upload TPM values with sample annotations
#

for taxid, species_id in curr_species_id_map.items():
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    gene_label_id_map = gene_controller.get_label_id_map()

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
        gene_id_map=gene_label_id_map,
        sa_type=SampleAnnotationType.PO,
        sample_labels=tpm_parser.get_sample_labels(),
        sa_assignments=sa_assignment_parser.get_sample_annotation_map(),
    )
    po_controller.upload_many(row_iterator=tpm_parser.parse())

    # Update SA entities with species id
    print(f"Updating po for taxid{taxid}")
    po_entity_controller.update_with_species(
        species_id,
        sa_assignment_parser.get_unique_sa_labels()
    )


#
# Upload sample annotation entities, tracking the species_ids
#
po_entity_controller.upload_all()


#
# Upload Gene Annotation Buckets
#


for taxid, species_id in curr_species_id_map.items():
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    gene_label_id_map = gene_controller.get_label_id_map()
    #
    # MAPMAN
    #
    mapman_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.MAPMAN)
    mapman_id_map = mapman_ga_controller.get_label_id_map()

    print(f"Uploading MAPMAN assignments for taxid{taxid}")
    mapman_ga_bucket_controller = GeneAnnotationBucketController(
        species_id=species_id,
        ga_type=GeneAnnotationType.MAPMAN,
        ga_id_map=mapman_id_map,
        gene_id_map=gene_label_id_map
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
        species_id=species_id,
        ga_type=GeneAnnotationType.INTERPRO,
        ga_id_map=interpro_id_map,
        gene_id_map=gene_label_id_map,
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


# #
# # Update median SPMs
# #


# for taxid, species_id in curr_species_id_map.items():
#     print(f"Updating median based spms for taxid{taxid}")
#     gene_controller = GeneController(taxid=taxid, species_id=species_id)
#     gene_label_id_map = gene_controller.get_label_id_map()

#     sa_updater = SampleAnnotationSpmUpdater(
#         species_id=species_id,
#         gene_id_map=gene_label_id_map,
#         sa_type=SampleAnnotationType.PO,
#     )
#     sa_updater.update_median_spms()
