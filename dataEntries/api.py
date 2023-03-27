import dataclasses
from typing import Dict, Tuple

from dataclasses_json import dataclass_json

from basic import DataTraitInstance, DataTrait
from dataEntries import DataEntriesAdapter
from dataTraitManagement.api import get_data_traits_for_management, DataTraitManagement


@dataclass_json
@dataclasses.dataclass
class DataEntry:
    id: str
    instances: list[DataTraitInstance]


class TraitNotKnownError(Exception):
    pass


class WorkflowDataEntry:
    payload: DataEntry
    user_passed_traits: Dict[str, Tuple[DataTrait, DataTraitInstance]]

    def __init__(self, payload: DataEntry):
        self.missing_traits = {}
        self.user_passed_traits = {}

        self.job_new_inserts = []
        self.job_delete = []
        self.job_update = []

        self.payload = payload

        # Traits currently in the database
        self.implemented_traits, self.known_trait_defs = capture_state(self.payload.id)

    def verify_trait_existence(self):
        for instance in self.payload.instances:
            if instance.title not in self.known_trait_defs:
                raise TraitNotKnownError()

    def fill_user_passed_traits(self):
        for instance in self.payload.instances:
            if instance.title not in self.implemented_traits:
                # new trait
                self.user_passed_traits[instance.title] = (self.known_trait_defs[instance.title].versions[0], instance)
            else:
                trait_versioned_def = self.known_trait_defs[instance.title].search_version(
                    self.implemented_traits[instance.title])
                try:
                    trait_versioned_def.validate(instance)
                    self.user_passed_traits[instance.title] = (trait_versioned_def, instance)
                except AssertionError:
                    self.user_passed_traits[instance.title] = (
                        self.known_trait_defs[instance.title].versions[0], instance)

    def fill_joblists(self):
        for (title, (dt, di)) in self.user_passed_traits.items():
            if di.title not in self.implemented_traits:
                # absolutly new insert
                self.job_new_inserts += [(dt, di)]
            elif dt.version != self.implemented_traits[title]:
                # there is a new version, unregister the old one
                self.job_delete += [
                    (self.known_trait_defs[dt.title].search_version(self.implemented_traits[title]))]
                # register the new version
                self.job_new_inserts += [(dt, di)]
            else:
                self.job_update += [(dt, di)]
        for instance in self.implemented_traits:
            if instance not in self.user_passed_traits:
                self.job_delete += [
                    (self.known_trait_defs[instance].search_version(self.implemented_traits[instance]))]

    def verify_trait_instances(self):
        # validate update_traits and new_traits
        for (title, (trait, instance)) in self.user_passed_traits.items():
            trait.validate(instance)


def capture_state(entry_id: str) -> Tuple[Dict[str, int], Dict[str, DataTraitManagement]]:
    implemented_traits = dict(
        [(trait_name, int(version)) for (version, trait_name) in DataEntriesAdapter.fetch_all_implementations(entry_id)])
    known_trait_defs = dict([(x.title, x) for x in get_data_traits_for_management()])
    return implemented_traits, known_trait_defs
