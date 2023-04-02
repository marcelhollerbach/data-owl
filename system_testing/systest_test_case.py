from unittest import TestCase

from system_testing.base import delete


class SystestCase(TestCase):
    cleanup_datamanagement: list[str] = []
    cleanup_ids: list[str] = []

    def tearDown(self):
        ids = self.cleanup_ids.copy()
        for id in ids:
            delete(f"v1/dataEntry/{id}")
        dtm = self.cleanup_datamanagement.copy()
        for dt in dtm:
            delete(f"v1/dataTraitManagement/{dt}")

