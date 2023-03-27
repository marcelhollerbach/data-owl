import dataclasses
import json

from apiflask import APIBlueprint
from dataclasses_json import dataclass_json
from flask import Response, request

from basic import DataTraitInstance
from basic.annotations import login_required
from dataEntries import adapter
from dataEntries.api import DataEntry, WorkflowDataEntry, TraitNotKnownError, capture_state
from dataTrait.api import MetaDataHelper
from dataTrait.db import DataTraitAdapter

routes = APIBlueprint('dataEntries', __name__)


@routes.route('/dataEntries', methods=['GET'])
@login_required
def list_all_entries():
    """
    List all data entries that are known and alive.

    Alive here means that the id did not get invalidated yet.
    The list contains he ID with all default fields.
    :return:
    """
    ids = TraitManagementAdapter.find_all_valid_ids()
    default_trait = DataTraitAdapter.DEFAULT
    enriched_ids = [{'id': elem_id} | default_trait.receive(elem_id).trait_instances for elem_id in ids]
    return Response(status=202, response=json.dumps(enriched_ids))


@routes.route('/dataEntry/<string:id>', methods=['GET'])
@login_required
def query_entry(entry_id: str):
    """
    Get the detail of a specific identifier

    This will return all instances of the traits

    :param entry_id: The ID of the entry
    :return:
    """
    if not TraitManagementAdapter.alive_id(entry_id):
        return Response(status=404)
    implemented_traits, known_trait_defs = capture_state(entry_id)
    impls = []
    for (title, version) in implemented_traits.items():
        trait_db = DataTraitAdapter.to_db_traits(known_trait_defs[title])
        impls.append(trait_db.receive(entry_id))
    return Response(status=202, response=DataEntryResult(id=entry_id, instances=impls).to_json())


def verify_assertions(entry: DataEntry):
    if 'Meta-Data' in [instance.title for instance in entry.instances]:
        return Response(status=400, response=MetaDataManagedBySystem().to_json())

    if 'Default' not in [instance.title for instance in entry.instances]:
        return Response(status=400, response=DefaultInstanceMissing().to_json())
    return None


@routes.route('/dataEntry/<string:id>', methods=['POST'])
@login_required
def update_entry(entry_id: str):
    if not TraitManagementAdapter.alive_id(entry_id):
        return Response(status=404)

    data_entry_dict = request.get_json()

    DataEntry.schema().load(data_entry_dict)
    entry: DataEntry = DataEntry.from_dict(data_entry_dict)

    if entry.id != entry_id:
        return Response(status=400, response=AmbigiousIdFields().to_json())

    response = verify_assertions(entry)
    if response is not None:
        return response

    workflow = WorkflowDataEntry(entry)
    try:
        workflow.verify_trait_existence()
    except TraitNotKnownError:
        return Response(status=400, response=TraitNotKnown().to_json())

    # Inject metadata for this entry
    workflow.payload.instances.append(MetaDataHelper.update(entry.id))

    workflow.fill_user_passed_traits()
    workflow.verify_trait_instances()

    assert 'Meta-Data' in workflow.user_passed_traits
    assert 'Meta-Data' not in [title for (title, _) in workflow.missing_traits]

    workflow.fill_joblists()

    commit_workflow(workflow)

    return Response(status=202, response=DataEntryPostReply(id=entry_id).to_json())


def commit_workflow(workflow):
    # Update existing content
    for (trait_def, instance) in workflow.job_update:
        trait_db = DataTraitAdapter.to_db_traits(trait_def)
        stored_instance = trait_db.receive(workflow.payload.id)
        if stored_instance != instance:
            trait_db.update(workflow.payload.id, instance.trait_instances)
    # insert all new traits and new versions
    for (trait, instance) in workflow.job_new_inserts:
        trait_db = DataTraitAdapter.to_db_traits(trait)
        trait_db.insert(workflow.payload.id, instance.trait_instances)
        TraitManagementAdapter.register_implementation(workflow.payload.id, trait)
    # delete all old traits
    for trait in workflow.job_delete:
        trait_db = DataTraitAdapter.to_db_traits(trait)
        trait_db.delete(workflow.payload.id)
        TraitManagementAdapter.unregister_implementation(workflow.payload.id, trait)


@routes.route('/dataEntry/<string:id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id: str):
    if not TraitManagementAdapter.alive_id(entry_id):
        return Response(status=404)
    implemented_traits, known_trait_defs = capture_state(entry_id)
    impls = []
    for (title, version) in implemented_traits.items():
        trait_db = DataTraitAdapter.to_db_traits(known_trait_defs[title])
        impls.append(trait_db.delete(entry_id))
    TraitManagementAdapter.invalidate_id(entry_id)
    return Response(status=202, response=DataEntryResult(id=entry_id, instances=impls).to_json())


@routes.route('/dataEntry', methods=['PUT'])
@login_required
def put_new_dc():
    data_entry_dict = request.get_json()

    data_entry_dict["id"] = ''

    DataEntry.schema().load(data_entry_dict)
    entry: DataEntry = DataEntry.from_dict(data_entry_dict)

    response = verify_assertions(entry)
    if response is not None:
        return response

    workflow = WorkflowDataEntry(entry)
    workflow.verify_trait_existence()

    # Inject metadata for this entry
    workflow.payload.instances.append(MetaDataHelper.create())

    workflow.fill_user_passed_traits()
    workflow.verify_trait_instances()

    assert 'Meta-Data' in workflow.user_passed_traits
    assert 'Meta-Data' not in [title for (title, _) in workflow.missing_traits]

    workflow.fill_joblists()
    workflow.payload.id = TraitManagementAdapter.register_id()

    commit_workflow(workflow)

    return Response(status=202, response=DataEntryPostReply(id=workflow.payload.id).to_json())


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
class AmbigiousIdFields:
    error: str = "ID in path is not equal to ID in payload"
    message: str = "The ID in the payload must be equal to the ID in the path"


@dataclass_json
@dataclasses.dataclass
class TraitNotKnown:
    error: str = "Trait not known"
    message: str = "A trait from the payload is not known"


@dataclass_json
@dataclasses.dataclass
class DefaultInstanceMissing:
    error: str = "DataEntry could not be created or updated"
    message: str = "The Default instance was not set. But it must."


@dataclass_json
@dataclasses.dataclass
class MetaDataManagedBySystem:
    error: str = "Meta-Data cannot be set"
    message: str = "The Meta-Data instance is set by the system, not by a caller."
