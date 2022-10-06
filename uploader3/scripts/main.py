from config.filepath_definitions import filepath_definitions
from uploader3.controllers import (
    SpeciesController,
    GeneController,
)
from uploader3.controllers import (
    GeneAnnotationController,
    GeneAnnotationBucketController,
)
from uploader3.models import (
    GeneAnnotationType,
)
from uploader3.parsers import (
    SpeciesParser,
    GeneParser,
    MapmanUnitParser,
    InterproUnitParser,
    GeneAnnotationAssignmentParser,
)


#
# Upload species
#


species_controller = SpeciesController()
species_parser = SpeciesParser(
    filepath=filepath_definitions.get_species_list_filepath()
)
species_controller.upload_many(species_parser.parse())
species_id_map = species_controller.get_taxid_id_map()


#
# Upload Gene Annotations
#


mapman_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.MAPMAN)
mapman_unit_parser = MapmanUnitParser(
    filepath=filepath_definitions.get_ga_filepath(ga_type=GeneAnnotationType.MAPMAN)
)
mapman_ga_controller.upload_many(mapman_unit_parser.parse())
mapman_id_map = mapman_ga_controller.get_label_id_map()


interpro_ga_controller = GeneAnnotationController(ga_type=GeneAnnotationType.INTERPRO)
interpro_unit_parser = InterproUnitParser(
    filepath=filepath_definitions.get_ga_filepath(ga_type=GeneAnnotationType.INTERPRO)
)
interpro_ga_controller.upload_many(interpro_unit_parser.parse())
interpro_id_map = interpro_ga_controller.get_label_id_map()


#
# Upload genes per species
#


for taxid, species_id in species_id_map.items():
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    gene_parser = GeneParser(
        filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
        species_id=species_id
    )
    gene_controller.upload_many(gene_parser.parse())
    label_id_map = gene_controller.get_label_id_map()


#
# Upload Gene Annotation Buckets
#

for taxid, species_id in species_id_map.items():
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    #
    # MAPMAN
    #
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

    #
    # INTERPRO
    #
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
