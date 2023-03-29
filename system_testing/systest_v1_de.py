import copy
import json
import logging
from unittest import TestCase

import requests

from basic import DataTraitInstance
from dataEntries.api import DataEntry
from routes.v1.de import DataEntryPostReply, DataEntryResult


def standard_headers():
    return {
        'Accept': 'application/json, text/plain, */*'
    }


def put(path: str, payload: any):
    return requests.put(f"http://localhost:5000/{path}",
                        json=payload.to_dict(),
                        headers=standard_headers())


def post(path: str, payload: any):
    return requests.post(f"http://localhost:5000/{path}",
                         json=payload.to_dict(),
                         headers=standard_headers())


def delete(path: str):
    return requests.delete(f"http://localhost:5000/{path}",
                           headers=standard_headers())


def get(path: str):
    return requests.get(f"http://localhost:5000/{path}",
                        headers=standard_headers())


STANDARD_PAYLOAD = DataEntry('1111-2222-3333-4444', [
    DataTraitInstance('Default', 1, {
        'Name': 'test',
        'Description': 'description',
        'State': 'OK'
    })
])


class TestV1De(TestCase):

    def create_standart_entry(self) -> DataEntryPostReply:
        res = put("v1/dataEntry", STANDARD_PAYLOAD)
        reply = DataEntryPostReply.from_dict(json.loads(res.content))
        self.assertEqual(res.status_code, 202)
        self.assertTrue(reply.id != '')
        self.assertTrue(reply.id != '1111-2222-3333-4444')
        logging.info(f"Test created {reply.id}")
        return reply

    def get_entry(self, reply):
        res_get = get(f"v1/dataEntry/{reply.id}")
        self.assertTrue(res_get.status_code, 202)
        get_reply = DataEntryResult.from_dict(json.loads(res_get.content))
        return get_reply

    def delete_entry(self, reply):
        res2 = delete(f"v1/dataEntry/{reply.id}")
        self.assertEqual(res2.status_code, 202)

    def test_create_and_delete(self):
        reply = self.create_standart_entry()
        logging.info(f"Test created {reply.id}")
        get_reply = self.get_entry(reply)
        self.assertEqual(get_reply.id, reply.id)
        self.assertEqual(STANDARD_PAYLOAD.instances[0], get_reply.instances[0])
        self.delete_entry(reply)
        res3 = delete(f"v1/dataEntry/{reply.id}")
        self.assertEqual(res3.status_code, 404)

    def test_wrong_delete_request(self):
        res = delete(f"v1/delete/111-222-3334-4444")
        self.assertEqual(res.status_code, 404)

    def test_update_of_default(self):
        reply = self.create_standart_entry()
        logging.info(f"Test created {reply.id}")
        payload = copy.deepcopy(STANDARD_PAYLOAD)
        payload.id = reply.id
        payload.instances[0].trait_instances['Name'] = 'HALLO'
        res = post(f"v1/dataEntry/{reply.id}", payload)
        self.assertEqual(res.status_code, 202)
        get_reply = self.get_entry(reply)
        self.assertEqual(get_reply.id, reply.id)
        self.assertEqual(payload.instances[0], get_reply.instances[0])
        self.delete_entry(reply)

    def test_update_of_meta(self):
        reply = self.create_standart_entry()
        logging.info(f"Test created {reply.id}")
        payload = copy.deepcopy(STANDARD_PAYLOAD)
        payload.id = reply.id
        payload.instances.append(DataTraitInstance(
            'Meta-Data', 1, {
                'Creator': 'bla@something.com',
                'Updater': 'bla@something.com',
                'Invalidator': ''
            }
        ))
        res = post(f"v1/dataEntry/{reply.id}", payload)
        self.assertEqual(res.status_code, 400)
        self.delete_entry(reply)

    def test_update_missing_default(self):
        reply = self.create_standart_entry()
        logging.info(f"Test created {reply.id}")
        payload = copy.deepcopy(STANDARD_PAYLOAD)
        payload.id = reply.id
        payload.instances = []
        res = post(f"v1/dataEntry/{reply.id}", payload)
        self.assertEqual(res.status_code, 400)
        self.delete_entry(reply)

    def test_update_missing_trait(self):
        reply = self.create_standart_entry()
        logging.info(f"Test created {reply.id}")
        payload = copy.deepcopy(STANDARD_PAYLOAD)
        payload.id = reply.id
        payload.instances.append(DataTraitInstance(
            'blabla', 1, {}
        ))
        res = post(f"v1/dataEntry/{reply.id}", payload)
        self.assertEqual(res.status_code, 400)
        self.delete_entry(reply)
