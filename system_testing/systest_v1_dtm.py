import uuid
from copy import deepcopy

from basic import DataTrait, TraitAttribute, Formats
from system_testing.base import put, get, delete, post, STANDARD_DATATRAIT
from system_testing.systest_test_case import SystestCase


class TestV1De(SystestCase):

    def assertUpstreamDTM(self, payload: DataTrait):
        res = get(f"v1/dataTraitManagement/{payload.title}")
        trait = DataTrait.from_json(res.content)
        self.assertEqual(trait, payload)

    def forkADataTrait(self) -> DataTrait:
        derivation = deepcopy(STANDARD_DATATRAIT)
        derivation.title = f"TestTrait{uuid.uuid4()}"
        return derivation

    def test_create_and_delete(self):
        derivation = self.forkADataTrait()

        d2 = deepcopy(derivation)
        d2.version = 20
        d2.author = "blabla"

        res = put("v1/dataTraitManagement/", d2)
        self.assertEqual(res.status_code, 202)

        self.assertUpstreamDTM(derivation)

        res = delete(f"v1/dataTraitManagement/{derivation.title}")
        self.assertEqual(res.status_code, 202)

    def test_failures_in_creates(self):
        derivation = self.forkADataTrait()

        res = put("v1/dataTraitManagement/", derivation)
        self.assertEqual(res.status_code, 202)
        self.cleanup_datamanagement.append(derivation.title)
        res = put("v1/dataTraitManagement/", derivation)
        self.assertEqual(res.status_code, 400)

        derivation.title = 'Default'
        res = put("v1/dataTraitManagement/", derivation)
        self.assertEqual(res.status_code, 400)

        derivation.title = 'Meta-Data'
        res = put("v1/dataTraitManagement/", derivation)
        self.assertEqual(res.status_code, 400)

    def test_update_persistant_version(self):
        payload = self.forkADataTrait()

        res = put("v1/dataTraitManagement/", payload)
        self.assertEqual(res.status_code, 202)
        self.cleanup_datamanagement.append(payload.title)
        derivation = deepcopy(payload)
        derivation.description = "SOMETHING-NEW"

        res = post(f"v1/dataTraitManagement/{payload.title}", derivation)
        self.assertEqual(res.status_code, 202)

        self.assertUpstreamDTM(derivation)

    def test_update_version_update(self):
        payload = self.forkADataTrait()

        res = put("v1/dataTraitManagement/", payload)
        self.assertEqual(res.status_code, 202)
        self.cleanup_datamanagement.append(payload.title)
        derivation = deepcopy(payload)
        derivation.description = "SOMETHING-NEW"
        derivation.fields.append(TraitAttribute(name='test', description='bla', format=Formats.SIMPLE_STRING))

        res = post(f"v1/dataTraitManagement/{payload.title}", derivation)
        self.assertEqual(res.status_code, 202)

        derivation.version = 1
        self.assertUpstreamDTM(derivation)
