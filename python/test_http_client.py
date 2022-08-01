from http_client import HttpClient
from client import TrainId, Seat


def test_http_client() -> None:
    train_id = TrainId("express_2000")
    client = HttpClient()
    client.reset(train_id)

    manifest = client.get_manifest(train_id)

    actual_seats = manifest.seats()
    assert len(actual_seats) == 16
    for seat in actual_seats:
        assert seat.is_free
