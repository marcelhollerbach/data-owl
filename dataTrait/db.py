import dataclasses
import logging

from dataclasses_json import dataclass_json

from basic import DataTrait, DataTraitInstance
from basic.db import get_db_connection
from dataTraitManagement.api import hardcoded_default, \
    get_user_managed_data_traits_versions


def gen_table_decl(trait: DataTrait) -> (str, str, str):
    title = trait.title.replace("-", "_")
    attr_list = [field.name.replace("-", "_") for field in trait.fields]
    attributes = ",".join(["id"] + attr_list)
    return f"dt_{str(title).lower()}_{trait.version}({attributes})", ",".join(
        ["?"] * (len(attr_list) + 1)), f"dt_{str(title).lower()}_{trait.version}"


@dataclass_json
@dataclasses.dataclass
class TraitDoesNotHaveData(Exception):
    title: str
    message: str

    def __init__(self, title: str, message: str):
        self.title = title
        self.message = message


class DataTraitDBOperation:
    def __init__(self, trait: DataTrait):
        self.trait = trait
        self.table_decl = gen_table_decl(self.trait)

    def insert(self, entry_id: str, instance: dict[str, str]):
        """
        Insert a specific instance of a trait
        :param entry_id: The id which is reserved for this data entry
        :param instance: The values of the instance, not going to be validated
        """
        values = [entry_id] + [value for value in instance.values()]
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"INSERT INTO {self.table_decl[0]} values ({self.table_decl[1]})", values)
        con.commit()

    def receive(self, entry_id: str) -> DataTraitInstance:
        """
        Get the values of this trait.

        Get the values of this trait for the given id. This does not validate that there is actually
        an instance of this.
        :param entry_id: The id of the data Entry
        :return: The instance of this data trait.
        """
        attr_list = [field.name for field in self.trait.fields]
        id_list = ",".join([attr.replace("-", "_") for attr in attr_list])
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"SELECT {id_list} FROM {self.table_decl[2]} WHERE id=?", (entry_id,))
        received_data = cur.fetchone()
        if received_data is None:
            raise TraitDoesNotHaveData("Trait not defined on ID",
                                       f"The trait {self.trait} is not defined on {entry_id}")
        else:
            instance = dict(zip(attr_list, list(received_data)))
            return DataTraitInstance(title=self.trait.title, trait_instances=instance)

    def update(self, entry_id: str, instance: dict[str, str]):
        """
        Update a specific instance of a trait
        :param entry_id: The id which is reserved for this data entry
        :param instance: The values of the instance, not going to be validated
        """
        # FIXME that is a hack
        self.delete(entry_id)
        self.insert(entry_id, instance)

    def delete(self, entry_id: str):
        """
        Delete this trait instance for the given id.
        :param entry_id: The id of the data Entry
        """
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"DELETE FROM {self.table_decl[2]} WHERE id=?", (entry_id,))
        con.commit()

    def usages(self) -> int:
        """
        Count how often
        """
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"SELECT count(id) FROM {self.table_decl[2]} GROUP BY ID")
        result = cur.fetchone()
        return result[0]


class DataTraitAdapter:
    @staticmethod
    def flush_data_trait_tables():
        """
        Ensure that all tables in the DB exists as it is described in the meta model
        """
        con = get_db_connection()
        cur = con.cursor()
        for value in get_user_managed_data_traits_versions():
            table_decl = gen_table_decl(value)
            logging.debug("Creating table " + table_decl[0])
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table_decl[0]}")
        con.commit()

    @staticmethod
    def to_db_traits(dt: DataTrait) -> DataTraitDBOperation:
        return DataTraitDBOperation(dt)

    DEFAULT = to_db_traits(hardcoded_default[0])
    META_DATA = to_db_traits(hardcoded_default[1])
