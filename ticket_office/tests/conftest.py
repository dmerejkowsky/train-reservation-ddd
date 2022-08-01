from client import Client, TrainId, Manifest, Reservation
from http_client import HttpClient
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

    def make_reservation(self, reservation: Reservation) -> None:
        pass


@pytest.fixture
def fake_client(train_id: TrainId) -> FakeClient:
    client = FakeClient()
    return client


@pytest.fixture
def http_client(train_id: TrainId) -> HttpClient:
    client = HttpClient()
    client.reset(train_id)
    return client
