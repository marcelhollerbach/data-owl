import datetime
import uuid

from click import UUID

from basic import DataTrait
from basic.db import get_db_connection

DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def id_generator() -> UUID:
    return uuid.uuid4()


class DataEntriesAdapter:
    def __init__(self):
        pass

    def exists_id(self, id: str):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT valid_until FROM data_entries WHERE id = ?", (str(id),))
        return len(cur.fetchall()) == 1

    def alive_id(self, id: str):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT valid_until FROM data_entries WHERE id = ?", (str(id),))
        result = cur.fetchone()
        expire_date = datetime.datetime.strptime(result[0], DATE_FORMAT)
        return expire_date >= datetime.datetime.now()

    def valid_id(self, id: str):
        return self.exists_id(id) and self.alive_id(id)

    def find_all_valid_ids(self) -> list[str]:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT id, valid_from, valid_until FROM data_entries")
        result = cur.fetchall()
        return [x[0] for x in result if
                datetime.datetime.strptime(x[2], DATE_FORMAT) >= datetime.datetime.now()]

    def register_id(self) -> str:
        con = get_db_connection()
        uuid = id_generator()
        while self.exists_id(str(uuid)):
            uuid = id_generator()
        cur = con.cursor()
        cur.execute("INSERT INTO data_entries(id, valid_from, valid_until) values (?, ?, ?)",
                    (str(uuid), datetime.datetime.now(), datetime.datetime.max))
        return str(uuid)

    def register_vtable(self, id: str, trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("INSERT INTO data_vtable(id, version, trait_name) values (?, ?, ?)",
                    (id, trait.version, trait.title))
        con.commit()

    def unregister_vtable(self, id, trait: DataTrait):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("DELETE FROM data_vtable WHERE id=? and version=? and trait_name=?",
                    (id, trait.version, trait.title))
        con.commit()

    def invalidate(self, id):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("DELETE FROM data_entries WHERE id=?",
                    (id,))
        cur.execute("DELETE FROM data_vtable WHERE id=?",
                    (id,))
        con.commit()

    def fetch_all_implementations(self, id) -> list[(str, str)]:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM data_vtable WHERE id = ?", (str(id),))
        data_result = cur.fetchall()
        return [(line[1], line[2]) for line in data_result]

    def ensure_data(self):
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS data_entries(id, valid_from, valid_until)")
        cur.execute("CREATE TABLE IF NOT EXISTS data_vtable(id, version, trait_name)")
        con.commit()
