from config.filepath_definitions import test_filepath_definitions as filepath_definitions
from uploader3.controllers import (
    SpeciesController,
    GeneController,
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
