

from config.filepath_definitions import filepath_definitions
from uploader3.controllers import (
    SpeciesController,
    GeneController,
)
from uploader3.controllers import (
    GeneAnnotationController,
)
from uploader3.models import (
    GeneAnnotationType,
)
from uploader3.parsers import (
    SpeciesParser,
    GeneParser,
    MapmanUnitParser,
    InterproUnitParser,
)


# species_controller = SpeciesController()
# species_parser = SpeciesParser(
#     filepath=filepath_definitions.get_species_list_filepath()
# )
# species_controller.upload_many(species_parser.parse())
# species_id_map = species_controller.get_taxid_id_map()


# for taxid, species_id in species_id_map.items():
#     gene_controller = GeneController(taxid=taxid, species_id=species_id)
#     gene_parser = GeneParser(
#         filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
#         species_id=species_id
#     )
#     gene_controller.upload_many(gene_parser.parse())
#     label_id_map = gene_controller.get_label_id_map()


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
