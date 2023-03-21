import json

from flask import Blueprint, request, Response

from basic.annotations import login_required
from dataEntries.db import DataEntriesAdapter
from dataEntries.model import DataEntry, DataEntryPostReply, DataEntryResult, DefaultInstanceMissing
from dataTrait import adapter as trait_adapter
from dataTrait.api import find_relevant_traits
from dataTraitManagement.api import get_data_traits_versions

routes = Blueprint('dataEntries', __name__)

adapter = DataEntriesAdapter()


@routes.route('/dataEntries', methods=['GET'])
@login_required
def list_all_entries():
    ids = adapter.find_all_valid_ids()
    default_trait = trait_adapter.find_data_trait("Default")
    enriched_ids = [{'id': elem_id} | default_trait.receive(elem_id).trait_instances for elem_id in ids]
    return Response(status=202, response=json.dumps(enriched_ids))


@routes.route('/dataEntry/<string:id>', methods=['GET'])
@login_required
def query_entry(id: str):
    if not adapter.valid_id(id):
        return Response(status=404)
    implemented_traits = adapter.fetch_all_implementations(id)
    relevant_traits = find_relevant_traits(implemented_traits)
    impls = []
    for title in relevant_traits:
        trait_db = trait_adapter.find_data_trait(title)
        impls.append(trait_db.receive(id))
    return Response(status=202, response=DataEntryResult(id=id, instances=impls).to_json())


@routes.route('/dataEntry/<string:id>', methods=['POST'])
@login_required
def update_entry(id: str):
    if not adapter.valid_id(id):
        return Response(status=404)

    traits = get_data_traits_versions()

    data_entry_dict = request.get_json()

    DataEntry.schema().load(data_entry_dict)
    entry: DataEntry = DataEntry.from_dict(data_entry_dict)
    used_data_traits = entry.validate()

    # fetch all implemented traits
    implemented_traits = adapter.fetch_all_implementations(id)
    known_traits = find_relevant_traits(implemented_traits)

    # helper lists
    defined_names = [instance.title for instance in entry.instances]
    missing_traits = [trait for trait in known_traits if trait not in defined_names]

    if 'Default' not in defined_names:
        return Response(status=400, response=DefaultInstanceMissing().to_json())

    # calculate list of traits and how to work with them
    update_traits = [instance for instance in entry.instances if instance.title in known_traits]
    new_traits = [instance for instance in entry.instances if instance.title not in known_traits]
    delete_traits = [instance[1] for instance in implemented_traits if instance[1] in missing_traits]

    # update all existing trait instances
    for instance in update_traits:
        trait_db = trait_adapter.find_data_trait(instance.title)
        trait_db.update(id, instance.trait_instances)

    # insert all new traits
    for instance in new_traits:
        trait_db = trait_adapter.find_data_trait(instance.title)
        trait_db.insert(id, instance.trait_instances)
        adapter.register_vtable(id, used_data_traits[instance.title])

    # delete all old traits
    for instance in delete_traits:
        trait_db = trait_adapter.find_data_trait(instance)
        trait_db.delete(id)
        adapter.unregister_vtable(id, traits[instance])

    return Response(status=202, response=DataEntryPostReply(id=id).to_json())


@routes.route('/dataEntry/<string:id>', methods=['DELETE'])
@login_required
def delete_entry(id: str):
    if not adapter.valid_id(id):
        return Response(status=404)
    implemented_traits = adapter.fetch_all_implementations(id)
    relevant_traits = find_relevant_traits(implemented_traits)
    impls = []
    for title in relevant_traits:
        trait_db = trait_adapter.find_data_trait(title)
        impls.append(trait_db.delete(id))
    adapter.invalidate(id)
    return Response(status=202, response=DataEntryResult(id=id, instances=impls).to_json())


@routes.route('/dataEntry', methods=['PUT'])
@login_required
def put_new_dc():
    data_entry_dict = request.get_json()

    DataEntry.schema().load(data_entry_dict)
    entry: DataEntry = DataEntry.from_dict(data_entry_dict)
    used_data_traits = entry.validate()

    if len([x.title for x in entry.instances if x.title == 'Default']) != 1:
        return Response(status=400, response=DefaultInstanceMissing().to_json())

    registered_id = adapter.register_id()

    for instance in entry.instances:
        trait_db = trait_adapter.find_data_trait(instance.title)
        trait_db.insert(registered_id, instance.trait_instances)
        adapter.register_vtable(registered_id, used_data_traits[instance.title])

    return Response(status=202, response=DataEntryPostReply(id=registered_id).to_json())
