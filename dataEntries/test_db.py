import os
from unittest import TestCase

from flask import Flask

import basic.db
from basic import DataTrait, TraitAttribute, Formats
from dataEntries import DataEntriesAdapter

TEST_DATABASE = './data_entries_test_db.db'

trait = DataTrait(
    title="testTrait",
    description="This data is a tester.",
    version=12,
    fields=[
        TraitAttribute(name="Currency", description="The currency this price is measured in",
                       format=Formats.SIMPLE_STRING),
    ]
)


class TestDataEntriesAdapter(TestCase):

    def setUp(self) -> None:
        basic.db.DATABASE = TEST_DATABASE
        self.adapter = DataEntriesAdapter()
        self.app = Flask(__name__)
        with self.app.app_context():
            self.adapter.ensure_data()

    def test_exists_id(self):
        with self.app.app_context():
            self.assertFalse(self.adapter.exists_id('aaaa'))
            id = self.adapter.register_id()
            self.assertTrue(self.adapter.exists_id(id))
            self.adapter.invalidate_id(id)
            self.assertTrue(self.adapter.exists_id(id))
            self.adapter.delete_id(id)

    def test_alive_id(self):
        with self.app.app_context():
            self.assertFalse(self.adapter.alive_id('aaaa'))
            id = self.adapter.register_id()
            self.assertTrue(self.adapter.alive_id(id))
            self.adapter.invalidate_id(id)
            self.assertFalse(self.adapter.alive_id(id))
            self.adapter.delete_id(id)

    def test_find_all_valid_ids(self):
        with self.app.app_context():
            id1 = self.adapter.register_id()
            id2 = self.adapter.register_id()
            self.assertEqual(set(self.adapter.find_all_valid_ids()), {id1, id2})
            self.adapter.invalidate_id(id1)
            self.assertEqual(set(self.adapter.find_all_valid_ids()), {id2})
            self.adapter.delete_id(id1)
            self.adapter.delete_id(id2)

    def test_register_id(self):
        with self.app.app_context():
            self.assertEqual(len(self.adapter.find_all_valid_ids()), 0)
            id1 = self.adapter.register_id()
            self.assertEqual(set(self.adapter.find_all_valid_ids()), {id1})
            self.adapter.delete_id(id1)

    def test_invalidate_id(self):
        with self.app.app_context():
            self.assertEqual(len(self.adapter.find_all_valid_ids()), 0)
            id1 = self.adapter.register_id()
            self.assertEqual(set(self.adapter.find_all_valid_ids()), {id1})
            self.adapter.invalidate_id(id1)
            self.assertEqual(len(self.adapter.find_all_valid_ids()), 0)
            self.adapter.delete_id(id1)

    def test_delete_id(self):
        with self.app.app_context():
            id1 = self.adapter.register_id()
            self.assertEqual(set(self.adapter.find_all_valid_ids()), {id1})
            self.adapter.delete_id(id1)
            self.assertFalse(self.adapter.exists_id(id1))
            self.adapter.delete_id(id1)

    def test_register_implementation(self):
        with self.app.app_context():
            id1 = self.adapter.register_id()
            self.adapter.register_implementation(id1, trait)
            self.assertEqual(self.adapter.fetch_all_implementations(id1), [(12, "testTrait")])
            self.adapter.delete_id(id1)

    def test_unregister_implementation(self):
        with self.app.app_context():
            id1 = self.adapter.register_id()
            self.adapter.register_implementation(id1, trait)
            self.assertEqual(self.adapter.fetch_all_implementations(id1), [(12, "testTrait")])
            self.adapter.unregister_implementation(id1, trait)
            self.assertEqual(self.adapter.fetch_all_implementations(id1), [])
            self.adapter.delete_id(id1)

    def test_fetch_all_implementations(self):
        with self.app.app_context():
            id1 = self.adapter.register_id()
            self.adapter.register_implementation(id1, trait)
            self.assertEqual(self.adapter.fetch_all_implementations(id1), [(12, "testTrait")])
            self.adapter.invalidate_id(id1)
            # we contain the implementations, its only invalidating the uuids
            self.assertEqual(self.adapter.fetch_all_implementations(id1), [(12, "testTrait")])
            self.adapter.delete_id(id1)

    def test_fetch_all_implementors(self):
        with self.app.app_context():
            id1 = self.adapter.register_id()
            id2 = self.adapter.register_id()
            self.adapter.register_implementation(id1, trait)
            self.adapter.register_implementation(id2, trait)
            self.assertEqual(set(self.adapter.fetch_all_implementors(trait)), {id1, id2})
            self.adapter.invalidate_id(id1)
            self.assertEqual(set(self.adapter.fetch_all_implementors(trait)), {id2})

    def tearDown(self) -> None:
        os.remove(TEST_DATABASE)
