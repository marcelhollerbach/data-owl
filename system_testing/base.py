import requests

from basic import DataTraitInstance, DataTrait, TraitAttribute, Formats
from dataEntries.api import DataEntry


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
STANDARD_DATATRAIT = DataTrait(
    author="mail@bu5hm4n.de",
    title="TestDataTrait",
    description="A test trait.",
    version=0,
    fields=[TraitAttribute(name="Currency", description="The currency this price is measured in",
                           format=Formats.SIMPLE_STRING), ]
)
