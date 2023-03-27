import os
from unittest import TestCase

from flask import Flask

import basic.db
from basic import DataTrait, TraitAttribute, Formats
from dataTraitManagement import TraitManagementAdapter

TEST_DATABASE = './test_db.db'


class TestTraitAdapter(TestCase):
    def setUp(self) -> None:
        basic.db.DATABASE = TEST_DATABASE
        self.adapter = TraitManagementAdapter()
        self.app = Flask(__name__)
        with self.app.app_context():
            self.adapter.ensure_data()

    def test_create_trait(self):
        trait = DataTrait(
            title="testTrait",
            description="This data is a tester.",
            version=1,
            author='asdf',
            fields=[
                TraitAttribute(name="Currency", description="The currency this price is measured in",
                               format=Formats.SIMPLE_STRING),
            ]
        ),
        with self.app.app_context():
            self.adapter.create_trait(trait[0], author='asdf')
            result = self.adapter.get_trait(trait[0].title, trait[0].version)
            self.assertEqual(len(trait[0].fields), len(result.fields))
            self.assertEqual(trait[0].fields[0], result.fields[0])
            self.assertEqual(trait[0].title, result.title)
            self.assertEqual(trait[0].description, result.description)
            self.assertEqual(trait[0].version, result.version)
            self.adapter.delete_trait(trait[0].title)

    def tearDown(self) -> None:
        os.remove(TEST_DATABASE)
