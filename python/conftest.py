from client import Client, TrainId, Manifest
import pytest


@pytest.fixture
def train_id() -> TrainId:
    return TrainId("express_2000")


class FakeClient(Client):
    def __init__(self) -> None:
        self.manifest = Manifest.empty()

    def set_manifest(self, manifest: Manifest) -> None:
        self.manifest = manifest

    def get_manifest(self, train_id: TrainId) -> Manifest:
        return self.manifest


@pytest.fixture
def client() -> FakeClient:
    return FakeClient()
