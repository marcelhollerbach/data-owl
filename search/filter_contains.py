from dataEntries import DataEntriesAdapter
from dataEntries.api import capture_state
from dataTrait.db import DataTraitAdapter
from search.api import AbstractFilter, VerificationException


class ContainsFilter(AbstractFilter):
    filter_name = "contains"

    def __init__(self, value):
        super().__init__(value)

    def verify(self):
        if not self.value.isalnum():
            raise VerificationException("Only alphanumberical searches are allowed")

    def apply_base(self) -> list[str]:
        all_ids = DataEntriesAdapter.find_all_valid_ids()
        return self.apply(all_ids)

    def apply(self, previous_state: list[str]) -> list[str]:
        result = []
        for entry_id in previous_state:
            implemented_traits, known_trait_defs = capture_state(entry_id)
            for (title, version) in implemented_traits.items():
                impl = DataTraitAdapter.to_db_traits(known_trait_defs[title])
                instance = impl.receive(entry_id)
                for v in instance.trait_instances.values():
                    if self.value in v:
                        result.append(entry_id)
        return result
