import dataclasses

from dataclasses_json import dataclass_json

from basic import DataTraitInstance, DataTrait
from dataTraitManagement.api import get_data_traits_versions


@dataclass_json
@dataclasses.dataclass
class DataEntry:
    id: str
    instances: list[DataTraitInstance]

    def validate(self) -> dict[str, DataTrait]:
        traits = get_data_traits_versions()
        result = {}
        for instance in self.instances:
            traits[instance.title].validate(instance)
            result[instance.title] = traits[instance.title]
        return result


@dataclass_json
@dataclasses.dataclass
class DataEntryResult:
    id: str
    instances: list[DataTraitInstance]


@dataclass_json
@dataclasses.dataclass
class DataEntryPostReply:
    id: str


@dataclass_json
@dataclasses.dataclass
class DefaultInstanceMissing:
    error: str = "DataEntry could not be created or updated"
    message: str = "The Default instance was not set. But it must."
