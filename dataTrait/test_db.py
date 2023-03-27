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
        self.app = Flask(__name__)
        with self.app.app_context():
            DataEntriesAdapter.ensure_data()
            TraitManagementAdapter.ensure_data()
            TraitManagementAdapter.create_trait(trait, author='asdf')

    def tearDown(self) -> None:
        os.remove(TEST_DATABASE)

    def test_flush_data_trait_tables(self):
        with self.app.app_context():
            DataTraitAdapter.flush_data_trait_tables()


class TestTraitAdapterPosition(TestCase):

    def setUp(self) -> None:
        basic.db.DATABASE = TEST_DATABASE
        self.app = Flask(__name__)
        with self.app.app_context():
            TraitManagementAdapter.ensure_data()
            DataEntriesAdapter.ensure_data()
            TraitManagementAdapter.create_trait(trait, author='asdf')
            DataTraitAdapter.flush_data_trait_tables()
            self.obj = TEST_TRAIT_ADAPTER

    def tearDown(self) -> None:
        os.remove(TEST_DATABASE)

    def test_insert(self):
        with self.app.app_context():
            entry_id = DataEntriesAdapter.register_id()
            self.obj.insert(entry_id, {
                "currency": "EUR"
            })
            obj = self.obj.receive(entry_id)
            self.assertEqual(obj.title, 'testTrait')
            self.assertEqual(obj.trait_instances, {"currency": "EUR"})

    def test_update(self):
        with self.app.app_context():
            entry_id = DataEntriesAdapter.register_id()
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
            entry_id = DataEntriesAdapter.register_id()
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
