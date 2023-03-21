from typing import Any

from basic import DataTrait, TraitAttribute
from basic.db import get_db_connection


class TraitAdapter():
    def __init__(self):
        pass

    def ensure_data(self):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS data_trait(id integer primary key autoincrement, title, description, version)")
        cur.execute("CREATE TABLE IF NOT EXISTS data_trait_attribute(id, name, description, format)")
        con.commit()

    def create_trait(self, trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("INSERT INTO data_trait(title, description, version) VALUES (?, ?, ?)",
                    (trait.title, trait.description, trait.version))
        id = cur.lastrowid
        for field in trait.fields:
            cur.execute("INSERT INTO data_trait_attribute(id, name, description, format) VALUES (?, ?, ?, ?)",
                        (id, field.name, field.description, field.format))
        con.commit()

    def update_trait_fields(self, trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT id FROM data_trait WHERE title = ? order by version desc",
                    (trait.title,))
        id = cur.fetchone()
        for field in trait.fields:
            cur.execute("UPDATE data_trait_attribute SET description = ? WHERE id = ? and name = ?",
                        (field.description, id[0], field.name))
        con.commit()

    def find_id(self, title: str, version: int | None = None) -> Any | None:
        con = get_db_connection()
        cur = con.cursor()
        if version is None:
            cur.execute("SELECT id, version FROM data_trait WHERE title=? order by version desc", (title,))
        else:
            cur.execute("SELECT id, version FROM data_trait WHERE title=? and version=?", (title, version,))
        id = cur.fetchone()
        if id is None:
            return None
        else:
            return id

    def delete_trait(self, title: str):
        con = get_db_connection()
        cur = con.cursor()
        id = self.find_id(title)
        cur.execute("DELETE FROM data_trait WHERE id=?", (id[0],))
        cur.execute("DELETE FROM data_trait_attribute WHERE id=?", (id[0],))
        con.commit()

    def get_all_traits(self) -> list[(str, int)]:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT title, version FROM data_trait")
        all_traits = cur.fetchall()
        return all_traits

    def get_trait(self, title: str, version: int) -> DataTrait:
        con = get_db_connection()
        cur = con.cursor()
        id = self.find_id(title, version)
        cur.execute("SELECT description FROM data_trait WHERE id=?", (id[0],))
        data_trait_result = cur.fetchone()
        cur.execute("SELECT name, description, format FROM data_trait_attribute WHERE id=?", (id[0],))
        data_trait_attributes = cur.fetchall()
        fields = [TraitAttribute(name=attribute[0], description=attribute[1], format=attribute[2]) for attribute in
                  data_trait_attributes]

        return DataTrait(title=title, description=data_trait_result[0], version=version, fields=fields)

    def update_description(self, trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT version FROM data_trait WHERE title = ? order by version desc",
                    (trait.title,))
        version = cur.fetchone()
        cur.execute("UPDATE data_trait SET description = ? WHERE title = ? and version = ?",
                    (trait.description, trait.title, int(version[0])))
        con.commit()
