import os
from unittest import TestCase

import pytest
from flask import Flask

import basic.db
from basic import DataTrait, TraitAttribute, Formats
from dataEntries import DataEntriesAdapter
from dataTrait.db import TraitDoesNotHaveData, DataTraitAdapter
from dataTraitManagement import TraitManagementAdapter

TEST_DATABASE = './data_trait_test_db.db'

trait = DataTrait(
    title="testTrait",
    description="This data is a tester.",
    version=12,
    author='asdf',
    fields=[
        TraitAttribute(name="currency", description="The currency this price is measured in",
                       format=Formats.SIMPLE_STRING),
    ]
)

TEST_TRAIT_ADAPTER = DataTraitAdapter.to_db_traits(trait)


class TestTraitAdapter(TestCase):

    def setUp(self) -> None:
        basic.db.DATABASE = TEST_DATABASE
        self.adapter = DataTraitAdapter()
        self.adapter2 = DataEntriesAdapter()
        self.adapter3 = TraitManagementAdapter()
        self.app = Flask(__name__)
        with self.app.app_context():
            self.adapter2.ensure_data()
            self.adapter3.ensure_data()
            self.adapter3.create_trait(trait, author='asdf')

    def tearDown(self) -> None:
        os.remove(TEST_DATABASE)

    def test_flush_data_trait_tables(self):
        with self.app.app_context():
            self.adapter.flush_data_trait_tables()


class TestTraitAdapterPosition(TestCase):

    def setUp(self) -> None:
        basic.db.DATABASE = TEST_DATABASE
        adapter = DataTraitAdapter()
        self.adapter = adapter2 = DataEntriesAdapter()
        adapter3 = TraitManagementAdapter()
        self.app = Flask(__name__)
        with self.app.app_context():
            adapter3.ensure_data()
            adapter2.ensure_data()
            adapter3.create_trait(trait, author='asdf')
            adapter.flush_data_trait_tables()
            self.obj = TEST_TRAIT_ADAPTER

    def tearDown(self) -> None:
        os.remove(TEST_DATABASE)

    def test_insert(self):
        with self.app.app_context():
            entry_id = self.adapter.register_id()
            self.obj.insert(entry_id, {
                "currency": "EUR"
            })
            obj = self.obj.receive(entry_id)
            self.assertEqual(obj.title, 'testTrait')
            self.assertEqual(obj.trait_instances, {"currency": "EUR"})

    def test_update(self):
        with self.app.app_context():
            entry_id = self.adapter.register_id()
            self.obj.insert(entry_id, {
                "currency": "EUR"
            })
            self.obj.update(entry_id, {
                "currency": "BLABLA"
            })
            obj = self.obj.receive(entry_id)
            self.assertEqual(obj.title, 'testTrait')
            self.assertEqual(obj.trait_instances, {"currency": "BLABLA"})

    def test_delete(self):
        with self.app.app_context():
            entry_id = self.adapter.register_id()
            self.obj.insert(entry_id, {
                "currency": "EUR"
            })
            obj = self.obj.receive(entry_id)
            self.assertEqual(obj.title, 'testTrait')
            self.assertEqual(obj.trait_instances, {"currency": "EUR"})
            self.obj.delete(entry_id)
            with pytest.raises(TraitDoesNotHaveData) as e:
                self.assertIsNone(self.obj.receive(entry_id))
            self.assertTrue('not defined on' in e.value.title)
