import dataclasses
from typing import Dict

from apiflask import APIBlueprint
from dataclasses_json import dataclass_json
from flask import jsonify, request, Response

from basic import DataTrait, TraitAttribute
from basic.annotations import login_required, fetch_author
from dataTrait.db import DataTraitAdapter
from dataTraitManagement import TraitManagementAdapter
from dataTraitManagement.api import get_data_traits_for_management, \
    get_user_managed_data_traits_versions

routes = APIBlueprint('dataTraitManagement', __name__)


@routes.route('/dataTraitManagement/', methods=['GET'])
@login_required
def list_all_for_management_dcs():
    return jsonify(get_data_traits_for_management())


@routes.route('/dataTraitManagement/<string:name>', methods=['GET'])
@login_required
def get_management_dc_latest(name: str):
    return jsonify(get_user_managed_data_traits_versions(name)[0])


def find_name_error(title: str):
    error = NameInvalid()
    for c in title:
        if not c.isalnum() and c != '-':
            error.message = "Title is not considered good, try using a-zA-Z0-9 and '-'."
            return error
    if len(title) <= 0:
        error.message = "Title must be longer than 0 characters"
        return error
    else:
        return None


def find_field_name_error(trait_update):
    for field in trait_update.fields:
        return find_name_error(field.name)


def calculate_lookup_dict(trait_instance: DataTrait) -> Dict[str, TraitAttribute]:
    return dict([(field.name + field.format, field) for field in trait_instance.fields])


@routes.route('/dataTraitManagement/<string:name>', methods=['POST'])
@login_required
def post_new_datatrait(name: str):
    data = request.get_json()
    data["author"] = fetch_author()

    DataTrait.schema().load(data)
    trait_update: DataTrait = DataTrait.from_dict(data)

    if name != trait_update.title:
        return Response(status=400, response=TitleImmutable().to_json())

    trait_info = TraitManagementAdapter.find_id(trait_update.title)
    if trait_info is None:
        return Response(status=400, response=BasicVersionNotFound().to_json())

    field_name_error = find_field_name_error(trait_update)
    if field_name_error is not None:
        return Response(status=400, response=field_name_error.to_json())

    trait_update.author = fetch_author()

    trait_instance = TraitManagementAdapter.get_trait(name, trait_info[1])
    if trait_instance.description != trait_update.description:
        TraitManagementAdapter.update_description(trait_update)

    original_fields = calculate_lookup_dict(trait_instance)
    update_fields = calculate_lookup_dict(trait_update)

    if len(original_fields.keys() - update_fields.keys()) == 0 and len(
            update_fields.keys() - original_fields.keys()) == 0:
        TraitManagementAdapter.update_trait_fields(trait_update)
    else:
        trait_update.version = trait_info[1] + 1
        TraitManagementAdapter.create_trait(trait_update, fetch_author())

    DataTraitAdapter.flush_data_trait_tables()

    return Response(status=202)


@routes.route('/dataTraitManagement/<string:name>', methods=['DELETE'])
@login_required
def delete_datatrait(name: str):
    trait_info = TraitManagementAdapter.find_id(name)
    if trait_info is None:
        return Response(status=400, response=BasicVersionNotFound().to_json())

    captured_state = get_data_traits_for_management(name)[0]
    for trait_version in captured_state.versions:
        trait_instance = DataTraitAdapter.to_db_traits(trait_version)
        if trait_instance.usages() > 0:
            return Response(status=400, response=TraitStillInUsage().to_json())

    TraitManagementAdapter.delete_trait(name)

    return Response(status=202)


@routes.route('/dataTraitManagement/', methods=['PUT'])
@login_required
def put_new_datatrait():
    data = request.get_json()

    data["author"] = fetch_author()
    data["version"] = 0

    DataTrait.schema().load(data)
    trait: DataTrait = DataTrait.from_dict(data)

    name_error = find_name_error(trait.title)
    if name_error is not None:
        return Response(status=400, response=name_error.to_json())

    if TraitManagementAdapter.find_id(trait.title) is not None:
        return Response(status=400, response=DuplicatedTitleVersion().to_json())

    field_name_error = find_field_name_error(trait)
    if field_name_error is not None:
        return Response(status=400, response=field_name_error.to_json())

    TraitManagementAdapter.create_trait(trait, trait.author)
    DataTraitAdapter.flush_data_trait_tables()

    return Response(status=202)


@dataclass_json
@dataclasses.dataclass
class TraitStillInUsage:
    error: str = "Trait is still in use!"
    message: str = "This trait is still being used!"


@dataclass_json
@dataclasses.dataclass
class TitleImmutable:
    error: str = "Title cannot be update"
    message: str = "The title of a trait is immutable, you cannot update it"


@dataclass_json
@dataclasses.dataclass
class BasicVersionNotFound:
    error: str = "Trait could not be updated"
    message: str = "Original version not found"


@dataclass_json
@dataclasses.dataclass
class NameInvalid:
    error: str = "Title did not fullfill all required rules"
    message: str = "--"


@dataclass_json
@dataclasses.dataclass
class LowerVersionNotThere:
    error: str = "Version illegal, as lower version is not there"
    message: str = "The version implies that there is a lower one, but this one is missing."


@dataclass_json
@dataclasses.dataclass
class DuplicatedTitleVersion:
    error: str = "Title and Version is already there"
    message: str = "Duplicated! The title and version is already there."
