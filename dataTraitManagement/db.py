from __future__ import annotations

NoneType = type(None)
from typing import Any, Union

from basic import DataTrait, TraitAttribute
from basic.db import get_db_connection


class TraitManagementAdapter:
    def __init__(self):
        pass

    @staticmethod
    def ensure_data():
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS data_trait"
            "(id integer primary key autoincrement, title, description, version, author)")
        cur.execute("CREATE TABLE IF NOT EXISTS data_trait_attribute(id, name, description, format)")
        con.commit()

    @staticmethod
    def create_trait(trait: DataTrait, author: str):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("INSERT INTO data_trait(title, description, version, author) VALUES (?, ?, ?, ?)",
                    (trait.title, trait.description, trait.version, author))
        entry_id = cur.lastrowid
        for field in trait.fields:
            cur.execute("INSERT INTO data_trait_attribute(id, name, description, format) VALUES (?, ?, ?, ?)",
                        (entry_id, field.name, field.description, field.format))
        con.commit()

    @staticmethod
    def update_trait_fields(trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT id FROM data_trait WHERE title = ? order by version desc",
                    (trait.title,))
        entry_id = cur.fetchone()
        for field in trait.fields:
            cur.execute("UPDATE data_trait_attribute SET description = ? WHERE id = ? and name = ?",
                        (field.description, entry_id[0], field.name))
        con.commit()

    @staticmethod
    def find_id(title: str, version: Union[int, NoneType] = None) -> Any | None:
        con = get_db_connection()
        cur = con.cursor()
        if version is None:
            cur.execute("SELECT id, version FROM data_trait WHERE title=? order by version desc", (title,))
        else:
            cur.execute("SELECT id, version FROM data_trait WHERE title=? and version=?", (title, version,))
        entry_id = cur.fetchone()
        if entry_id is None:
            return None
        else:
            return entry_id

    @staticmethod
    def delete_trait(title: str):
        con = get_db_connection()
        cur = con.cursor()
        entry_id = TraitManagementAdapter.find_id(title)
        cur.execute("DELETE FROM data_trait WHERE id=?", (entry_id[0],))
        cur.execute("DELETE FROM data_trait_attribute WHERE id=?", (entry_id[0],))
        con.commit()

    @staticmethod
    def get_all_traits() -> list[(str, int)]:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT title, version FROM data_trait")
        all_traits = cur.fetchall()
        return all_traits

    @staticmethod
    def get_trait(title: str, version: int) -> DataTrait:
        con = get_db_connection()
        cur = con.cursor()
        entry_id = TraitManagementAdapter.find_id(title, version)
        cur.execute("SELECT description, author FROM data_trait WHERE id=?", (entry_id[0],))
        data_trait_result = cur.fetchone()
        cur.execute("SELECT name, description, format FROM data_trait_attribute WHERE id=?", (entry_id[0],))
        data_trait_attributes = cur.fetchall()
        fields = [TraitAttribute(name=attribute[0], description=attribute[1], format=attribute[2]) for attribute in
                  data_trait_attributes]

        return DataTrait(title=title, description=data_trait_result[0], author=data_trait_result[1], version=version,
                         fields=fields)

    @staticmethod
    def update_description(trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT version FROM data_trait WHERE title = ? order by version desc",
                    (trait.title,))
        version = cur.fetchone()
        cur.execute("UPDATE data_trait SET description = ? WHERE title = ? and version = ?",
                    (trait.description, trait.title, int(version[0])))
        con.commit()
