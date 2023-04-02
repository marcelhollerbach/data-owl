from copy import deepcopy
from unittest import TestCase

from basic import DataTrait, TraitAttribute, Formats
from system_testing.base import put, get, delete, post

STANDARD_DATATRAIT = DataTrait(
    author="mail@bu5hm4n.de",
    title="TestDataTrait",
    description="A test trait.",
    version=0,
    fields=[TraitAttribute(name="Currency", description="The currency this price is measured in",
                           format=Formats.SIMPLE_STRING), ]
)


class TestV1De(TestCase):

    def test_create_and_delete(self):
        delete("v1/dataTraitManagement/TestDataTrait")
        delete("v1/dataTraitManagement/TestDataTrait")
        derivation = deepcopy(STANDARD_DATATRAIT)
        derivation.author = "blablabla"
        res = put("v1/dataTraitManagement/", derivation)
        self.assertEqual(res.status_code, 202)
        res = get("v1/dataTraitManagement/TestDataTrait")
        trait = DataTrait.from_json(res.content)
        self.assertEqual(trait, STANDARD_DATATRAIT)
        res = delete("v1/dataTraitManagement/TestDataTrait")
        self.assertEqual(res.status_code, 202)

    def test_update(self):
        delete("v1/dataTraitManagement/TestDataTrait")
        res = put("v1/dataTraitManagement/", STANDARD_DATATRAIT)
        self.assertEqual(res.status_code, 202)
        derivation = deepcopy(STANDARD_DATATRAIT)
        derivation.description = "SOMETHING-NEW"
        res = post("v1/dataTraitManagement/TestDataTrait", derivation)
        self.assertEqual(res.status_code, 202)
        res = get("v1/dataTraitManagement/TestDataTrait")
        trait = DataTrait.from_json(res.content)
        self.assertEqual(trait, derivation)
        res = delete("v1/dataTraitManagement/TestDataTrait")
        self.assertEqual(res.status_code, 202)
