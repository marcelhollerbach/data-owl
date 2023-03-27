from basic import DataTraitInstance
from basic.annotations import fetch_author
from dataTrait.db import DataTraitAdapter


class MetaDataHelper:
    @staticmethod
    def update(entry_id: str) -> DataTraitInstance:
        receiver = DataTraitAdapter.META_DATA.receive(entry_id)
        receiver.trait_instances['Updater'] = fetch_author()
        return receiver

    @staticmethod
    def create() -> DataTraitInstance:
        data = {
            'Creator': fetch_author(),
            'Updater': fetch_author(),
            'Invalidator': ''
        }

        return DataTraitInstance(title='Meta-Data', trait_instances=data)
