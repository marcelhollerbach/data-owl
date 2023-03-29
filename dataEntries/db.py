import datetime
import uuid

from typing import List, Tuple

from basic import DataTrait
from basic.db import get_db_connection

DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def id_generator() -> uuid.UUID:
    return uuid.uuid4()


class DataEntriesAdapter:
    def __init__(self):
        pass

    @staticmethod
    def exists_id(entry_id: str):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT valid_until FROM data_entries WHERE id = ?", (str(entry_id),))
        return len(cur.fetchall()) == 1

    @staticmethod
    def alive_id(entry_id: str):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT valid_until FROM data_entries WHERE id = ?", (str(entry_id),))
        result = cur.fetchone()
        if result is not None:
            expire_date = datetime.datetime.strptime(result[0], DATE_FORMAT)
            return expire_date >= datetime.datetime.now()
        else:
            return False

    @staticmethod
    def find_all_valid_ids() -> List[str]:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT id, valid_from, valid_until FROM data_entries")
        result = cur.fetchall()
        return [x[0] for x in result if
                datetime.datetime.strptime(x[2], DATE_FORMAT) >= datetime.datetime.now()]

    @staticmethod
    def register_id() -> str:
        con = get_db_connection()
        generated_uuid = id_generator()
        while DataEntriesAdapter.exists_id(str(generated_uuid)):
            generated_uuid = id_generator()
        cur = con.cursor()
        cur.execute("INSERT INTO data_entries(id, valid_from, valid_until) values (?, ?, ?)",
                    (str(generated_uuid), datetime.datetime.now(), datetime.datetime.max))
        return str(generated_uuid)

    @staticmethod
    def invalidate_id(entry_id):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("UPDATE data_entries SET valid_until = ? WHERE id=?",
                    (datetime.datetime.now(), entry_id,))
        con.commit()

    @staticmethod
    def delete_id(entry_id):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("DELETE FROM data_entries WHERE id=?",
                    (entry_id,))
        cur.execute("DELETE FROM data_vtable WHERE id=?",
                    (entry_id,))
        con.commit()

    @staticmethod
    def register_implementation(entry_id: str, trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("INSERT INTO data_vtable(id, version, trait_name) values (?, ?, ?)",
                    (entry_id, trait.version, trait.title))
        con.commit()

    @staticmethod
    def unregister_implementation(entry_id, trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("DELETE FROM data_vtable WHERE id=? and version=? and trait_name=?",
                    (entry_id, trait.version, trait.title))
        con.commit()

    @staticmethod
    def fetch_all_implementations(entry_id) -> List[Tuple[str, str]]:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT id, version, trait_name FROM data_vtable WHERE id = ?", (str(entry_id),))
        data_result = cur.fetchall()
        return [(line[1], line[2]) for line in data_result]

    @staticmethod
    def fetch_all_implementors(trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT dv.id, valid_until FROM data_vtable dv, data_entries de WHERE trait_name = ? and dv.id = de.id",
            (trait.title,))
        data_result = cur.fetchall()
        return [x[0] for x in data_result if
                datetime.datetime.strptime(x[1], DATE_FORMAT) >= datetime.datetime.now()]

    @staticmethod
    def ensure_data():
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS data_entries(id, valid_from, valid_until)")
        cur.execute("CREATE TABLE IF NOT EXISTS data_vtable(id, version, trait_name)")
        con.commit()
