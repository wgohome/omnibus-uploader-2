

from config.filepath_definitions import filepath_definitions
from uploader3.controllers import (
    SpeciesController,
    GeneController,
)
from uploader3.parsers import (
    SpeciesParser,
    GeneParser,
)


species_controller = SpeciesController()
species_parser = SpeciesParser(
    filepath=filepath_definitions.get_species_list_filepath()
)
# species_controller.upload_many(species_parser.parse())
species_id_map = species_controller.get_taxid_id_map()


for taxid, species_id in species_id_map.items():
    gene_controller = GeneController(taxid=taxid, species_id=species_id)
    gene_parser = GeneParser(
        filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
        species_id=species_id
    )
    gene_controller.upload_many(gene_parser.parse())
    gene_id_map = gene_controller.get_taxid_id_map()
