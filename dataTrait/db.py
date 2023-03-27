import dataclasses
import logging

from dataclasses_json import dataclass_json

from basic import DataTrait, DataTraitInstance
from basic.db import get_db_connection
from dataTraitManagement.api import get_data_traits_versions, get_data_traits_for_management


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


class DataTraitDBOperation():
    def __init__(self, trait: DataTrait):
        self.trait = trait
        self.table_decl = gen_table_decl(self.trait)

    def insert(self, id: str, instance: dict[str, str]):
        """
        Insert a specific instance of a trait
        :param id: The id which is reserved for this data entry
        :param instance: The values of the instance, not going to be validated
        """
        values = [id] + [value for value in instance.values()]
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"INSERT INTO {self.table_decl[0]} values ({self.table_decl[1]})", values)
        con.commit()

    def receive(self, id: str) -> DataTraitInstance:
        """
        Get the values of this trait.

        Get the values of this trait for the given id. This does not validate that there is actually
        an instance of this.
        :param id: The id of the data Entry
        :return: The instance of this data trait.
        """
        attr_list = [field.name for field in self.trait.fields]
        id_list = ",".join([attr.replace("-", "_") for attr in attr_list])
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"SELECT {id_list} FROM {self.table_decl[2]} WHERE id=?", (id,))
        all = cur.fetchone()
        if all is None:
            raise TraitDoesNotHaveData("Trait not defined on ID", f"The trait {self.trait} is not defined on {id}")
        else:
            instance = dict(zip(attr_list, list(all)))
            return DataTraitInstance(title=self.trait.title, trait_instances=instance)

    def update(self, id: str, instance: dict[str, str]):
        """
        Update a specific instance of a trait
        :param id: The id which is reserved for this data entry
        :param instance: The values of the instance, not going to be validated
        """
        # FIXME that is a hack
        self.delete(id)
        self.insert(id, instance)

    def delete(self, id: str):
        """
        Delete this trait instance for the given id.
        :param id: The id of the data Entry
        """
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"DELETE FROM {self.table_decl[2]} WHERE id=?", (id,))
        con.commit()

    def usages(self) -> int:
        """
        Count how often
        :param id: The id of the data Entry
        """
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"SELECT count(id) FROM {self.table_decl[2]} GROUP BY ID")
        result = cur.fetchone()
        return result[0]


class DataTraitAdapter:
    def flush_data_trait_tables(self):
        """
        Ensure that all tables in the DB exists as it is described in the meta model
        """
        con = get_db_connection()
        cur = con.cursor()
        for value in get_data_traits_versions().values():
            table_decl = gen_table_decl(value)
            logging.debug("Creating table " + table_decl[0])
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table_decl[0]}")
        con.commit()

    def find_data_trait(self, title: str, version: int | None = None) -> DataTraitDBOperation:
        """
        Receive the data trait db connection for a given data trait.
        Does not validate the existance of the trait.

        :param version:
        :param title: The title of the trait If None, the newest is taken
        :return: The db object for the data trait
        """
        trait = get_data_traits_for_management(title)[0]
        index = 0
        if version is not None:
            for i, trait_version in enumerate(trait.versions):
                if trait_version.version == version:
                    index = i
        return DataTraitDBOperation(trait.versions[index])
