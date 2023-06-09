from typing import List

from dataEntries import DataEntriesAdapter
from dataTraitManagement.api import get_data_traits_versions
from search.api import AbstractFilter, VerificationException


class TypeFilter(AbstractFilter):
    filter_name = "type"

    def __init__(self, value):
        super().__init__(value)

    def verify(self):
        traits = get_data_traits_versions().keys()
        if self.value not in traits:
            raise VerificationException(f"The type {self.value} is not defined",
                                        f"Available types are {','.join(traits)}")

    def apply_base(self) -> List[str]:
        traits = get_data_traits_versions()
        return DataEntriesAdapter.fetch_all_implementors(traits[self.value])

    def apply(self, previous_state: List[str]) -> List[str]:
        result = self.apply_base()
        return [x for x in previous_state if x in result]
