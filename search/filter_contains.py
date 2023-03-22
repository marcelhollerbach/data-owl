from dataEntries import adapter
from dataTrait import adapter as dt_adapter
from search.api import AbstractFilter, VerificationException, register_filter


class ContainsFilter(AbstractFilter):
    filter_name = "contains"

    def __init__(self, value):
        super().__init__(value)

    def verify(self):
        if not self.value.isalnum():
            raise VerificationException("Only alphanumberical searches are allowed")

    def apply_base(self) -> list[str]:
        all_ids = adapter.find_all_valid_ids()
        return self.apply(all_ids)

    def apply(self, previous_state: list[str]) -> list[str]:
        result = []
        for id in previous_state:
            implementations = set([impl[1] for impl in adapter.fetch_all_implementations(id)])
            for implementation in implementations:
                impl = dt_adapter.find_data_trait(implementation)
                instance = impl.receive(id)
                for v in instance.trait_instances.values():
                    if self.value in v:
                        result.append(id)
        return result

