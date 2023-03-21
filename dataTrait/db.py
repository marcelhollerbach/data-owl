import logging

from basic import DataTrait, DataTraitInstance
from basic.db import get_db_connection
from dataTraitManagement.api import get_data_traits_versions


def gen_table_decl(trait: DataTrait) -> (str, str, str):
    title = trait.title.replace("-", "_")
    attr_list = [field.name.replace("-", "_") for field in trait.fields]
    attributes = ",".join(["id"] + attr_list)
    return f"dt_{str(title).lower()}_{trait.version}({attributes})", ",".join(
        ["?"] * (len(attr_list) + 1)), f"dt_{str(title).lower()}_{trait.version}"


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
        Get the values of this trait for the given id. This does not validate that there is actually an instance of this.
        :param id: The id of the data Entry
        :return: The instance of this data trait.
        """
        attr_list = [field.name for field in self.trait.fields]
        id_list = ",".join([attr.replace("-", "_") for attr in attr_list])
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"SELECT {id_list} FROM {self.table_decl[2]} WHERE id=?", (id,))
        all = cur.fetchone()
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

    def find_data_trait(self, title: str) -> DataTraitDBOperation:
        """
        Receive the data trait db connection for a given data trait.
        Does not validate the existance of the trait.

        :param title: The title of the trait
        :return: The db object for the data trait
        """
        traits = get_data_traits_versions()
        assert title in traits
        trait = traits[title]
        return DataTraitDBOperation(trait)
