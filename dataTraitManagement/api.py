from dataclasses import dataclass
from typing import Union

from dataclasses_json import dataclass_json

from basic import DataTrait, TraitAttribute, Formats
from dataTraitManagement import adapter


@dataclass_json
@dataclass
class DataTraitManagement:
    title: str
    description: str
    immutable: bool
    versions: [DataTrait]


hardcoded_default = DataTrait(
    title="Default",
    description="The default you will have to enter.",
    version=1,
    fields=[
        TraitAttribute(name="Name", description="The name of the entry", format=Formats.SIMPLE_STRING),
        TraitAttribute(name="Description", description="A detailed description of the data",
                       format=Formats.SIMPLE_STRING),
        TraitAttribute(name="State", description="Describing the state of this entry.",
                       format=Formats.SIMPLE_STRING),
    ]
)

hardcoded_default_management = DataTraitManagement(
    title=hardcoded_default.title,
    description=hardcoded_default.description,
    immutable=True,
    versions=[hardcoded_default]
)


def get_data_traits_versions(searched_name: Union[str, None] = None) -> dict[str, DataTrait]:
    tmp_concat = [hardcoded_default]
    tmp_concat.extend(get_user_managed_data_traits_versions(searched_name))
    return dict((trait.title, trait) for trait in tmp_concat)


def get_user_managed_data_traits_versions(searched_name: Union[str, None] = None) -> list[DataTrait]:
    """
    Return all live data trait management object

    Return a list of Datatraits, all datatraits are defined in the newest version.

    :return: List of datatraits
    """
    managed_traits = get_all_traits_managed(searched_name)
    reduction_map = dict((k, max(v)) for k, v in managed_traits.items())
    return [adapter.get_trait(title, version) for (title, version) in reduction_map.items()]


def get_data_traits_for_management(searched_name: Union[str, None] = None) -> list[DataTraitManagement]:
    """
    Return all data trait management objects.

    One object defined all versions that ever got defined

    :return: List of Data Trait Managment objects
    """

    def map_to_data_trait_management(title: str, versions: list[int]) -> DataTraitManagement:
        """
        Map a title and a list of versions to a data trait management instance.
        :param title: The title of the trait
        :param versions: The versions that got defined
        :return: The object
        """
        instances = [adapter.get_trait(title, version) for version in versions]
        return DataTraitManagement(title=title, description=instances[-1].description, immutable=False,
                                   versions=instances)

    reduction_map = get_all_traits_managed(searched_name)
    return [map_to_data_trait_management(title, versions) for title, versions in reduction_map.items()] + [
        hardcoded_default_management]


def get_all_traits_managed(searched_name: Union[str, None]) -> dict[str, list[int]]:
    """
    Get a map with all traits and the defined versions
    :return: Dict that maps each trait name to a list of defined versions
    """

    def accepts(trait_name: str) -> bool:
        if isinstance(searched_name, str):
            return trait_name[0] == searched_name
        else:
            return True

    traits = [x for x in adapter.get_all_traits() if accepts(x)]
    reduction_map: dict[str, list[int]] = {}
    for trait in traits:
        if trait[0] in reduction_map:
            reduction_map[trait[0]].append(trait[1])
            reduction_map[trait[0]].sort()
        else:
            reduction_map[trait[0]] = [trait[1]]

    return reduction_map
