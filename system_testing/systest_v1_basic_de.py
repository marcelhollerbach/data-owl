import copy
import json
import logging
import uuid

from basic import DataTraitInstance, TraitAttribute, Formats
from dataEntries.api import DataEntry
from system_testing.base import put, post, delete, get, STANDARD_PAYLOAD, STANDARD_DATATRAIT
from system_testing.systest_test_case import SystestCase


class TestV1De(SystestCase):

    def fork_data_entry(self, reply: str):
        payload = copy.deepcopy(STANDARD_PAYLOAD)
        payload.id = reply
        return payload

    def create_standard_entry(self) -> str:
        res = put("v1/dataEntry", STANDARD_PAYLOAD)
        reply = json.loads(res.content)
        self.assertEqual(res.status_code, 202)
        self.assertTrue(reply != '')
        self.assertTrue(reply != '1111-2222-3333-4444')
        logging.info(f"Test created {reply}")
        self.cleanup_ids.append(reply)
        return reply

    def get_entry(self, reply):
        res_get = get(f"v1/dataEntry/{reply.id}")
        self.assertTrue(res_get.status_code, 202)
        get_reply = DataEntry.from_dict(json.loads(res_get.content))
        return get_reply

    def delete_entry(self, reply):
        res2 = delete(f"v1/dataEntry/{reply}")
        self.assertEqual(res2.status_code, 202)
        self.cleanup_ids.remove(reply)

    def create_some_datatrait(self, test_instance_title):
        derivation = copy.deepcopy(STANDARD_DATATRAIT)
        derivation.title = test_instance_title
        res = put("v1/dataTraitManagement/", derivation)
        self.assertEqual(res.status_code, 202)
        self.cleanup_datamanagement.append(derivation.title)
        return derivation

    def assertUpstreamDt(self, payload: DataEntry):
        get_reply = self.get_entry(payload)
        self.assertEqual(get_reply.id, payload.id)
        upstream_lookup_map = dict([(instance.title, instance) for instance in get_reply.instances])
        payload_lookup_map = dict([(instance.title, instance) for instance in payload.instances])

        del upstream_lookup_map['Meta-Data']

        self.assertSetEqual(set(upstream_lookup_map.keys()), set(payload_lookup_map.keys()))
        for keys in upstream_lookup_map.keys():
            self.assertEqual(upstream_lookup_map[keys], payload_lookup_map[keys])

    def test_create_and_delete(self):
        reply = self.create_standard_entry()
        logging.info(f"Test created {reply}")
        payload = self.fork_data_entry(reply)
        self.assertUpstreamDt(payload)
        self.delete_entry(reply)
        res3 = delete(f"v1/dataEntry/{reply}")
        self.assertEqual(res3.status_code, 404)

    def test_wrong_delete_request(self):
        res = delete(f"v1/delete/111-222-3334-4444")
        self.assertEqual(res.status_code, 404)

    def test_update_of_default(self):
        reply = self.create_standard_entry()
        logging.info(f"Test created {reply}")
        payload = self.fork_data_entry(reply)
        payload.instances[0].trait_instances['Name'] = 'HALLO'
        res = post(f"v1/dataEntry/{reply}", payload)
        self.assertEqual(res.status_code, 202)
        self.assertUpstreamDt(payload)

    def test_update_of_meta(self):
        reply = self.create_standard_entry()
        logging.info(f"Test created {reply}")
        payload = self.fork_data_entry(reply)
        payload.instances.append(DataTraitInstance(
            'Meta-Data', 1, {
                'Creator': 'bla@something.com',
                'Updater': 'bla@something.com',
                'Invalidator': ''
            }
        ))
        res = post(f"v1/dataEntry/{reply}", payload)
        self.assertEqual(res.status_code, 400)
        self.delete_entry(reply)

    def test_update_missing_default(self):
        reply = self.create_standard_entry()
        logging.info(f"Test created {reply}")
        payload = self.fork_data_entry(reply)
        payload.instances = []
        res = post(f"v1/dataEntry/{reply}", payload)
        self.assertEqual(res.status_code, 400)
        self.delete_entry(reply)

    def test_update_missing_trait(self):
        reply = self.create_standard_entry()
        logging.info(f"Test created {reply}")
        payload = self.fork_data_entry(reply)
        payload.instances.append(DataTraitInstance(
            'blabla', 1, {}
        ))
        res = post(f"v1/dataEntry/{reply}", payload)
        self.assertEqual(res.status_code, 400)
        self.delete_entry(reply)

    def test_attaching_detaching_new_trait(self):
        test_instance = DataTraitInstance(
            f'attachingTest{uuid.uuid4()}', 0, {
                'Currency': 'EUR'
            }
        )
        reply = self.create_standard_entry()
        logging.info(f"Test created {reply}")
        self.create_some_datatrait(test_instance.title)

        payload = self.fork_data_entry(reply)
        payload.instances.append(
            test_instance
        )

        res = post(f"v1/dataEntry/{payload.id}", payload)
        self.assertEqual(res.status_code, 202)
        self.assertUpstreamDt(payload)

        payload.instances.pop()
        res = post(f"v1/dataEntry/{payload.id}", payload)
        self.assertEqual(res.status_code, 202)
        self.assertUpstreamDt(payload)

    def test_version_upgrade(self):
        test_instance = DataTraitInstance(
            f'attachingTest{uuid.uuid4()}', 0, {
                'Currency': 'EUR'
            }
        )
        test_instance_upgraded = DataTraitInstance(
            test_instance.title, 1, {
                'Currency': 'EUR',
                'test': 'ehllo'
            }
        )
        reply = self.create_standard_entry()
        logging.info(f"Test created {reply}")
        dt = self.create_some_datatrait(test_instance.title)

        payload = self.fork_data_entry(reply)
        payload.instances.append(
            test_instance
        )

        res = post(f"v1/dataEntry/{payload.id}", payload)
        self.assertEqual(res.status_code, 202)

        # Upgrade datatrait
        dt.fields.append(TraitAttribute(name='test', description='bla', format=Formats.SIMPLE_STRING))
        res = post(f"v1/dataTraitManagement/{dt.title}", dt)
        self.assertEqual(res.status_code, 202)
        payload.instances.pop()
        payload.instances.append(test_instance_upgraded)

        # Upgrade dataentry
        res = post(f"v1/dataEntry/{payload.id}", payload)
        self.assertEqual(res.status_code, 202)
