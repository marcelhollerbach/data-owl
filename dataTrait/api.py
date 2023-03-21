from dataTraitManagement.api import get_data_traits_versions


def find_relevant_traits(implemented_traits: list[str]) -> list[str]:
    relevant_traits = []
    traits = get_data_traits_versions()
    for impl in implemented_traits:
        version = impl[0]
        name = impl[1]
        if traits[name].version == version:
            relevant_traits.append(name)
    return relevant_traits
