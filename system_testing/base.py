import requests

from basic import DataTraitInstance
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
