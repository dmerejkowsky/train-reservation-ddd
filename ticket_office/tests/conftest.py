import pytest

from client import CoachId, Seat, SeatId, SeatNumber, Train, TrainId
from http_client import HttpClient

from .helpers import FakeClient


def empty_seats_for_coach(coach_id: CoachId) -> list[Seat]:
    seat_numbers = [SeatNumber(i) for i in range(1, 10)]
    seat_ids = [SeatId(s, coach_id) for s in seat_numbers]
    seats = [Seat.free_seat_with_id(id) for id in seat_ids]
    return seats


def make_empty_train(train_id: TrainId) -> Train:
    coach_ids = [CoachId(c) for c in "ABCDEF"]
    seats = []
    for coach_id in coach_ids:
        seats.extend(empty_seats_for_coach(coach_id))
    return Train(id=train_id, seats=seats)


@pytest.fixture
def train_id() -> TrainId:
    return TrainId("express_2000")


@pytest.fixture
def train(train_id: TrainId) -> Train:
    train_id = TrainId("express_2000")
    return make_empty_train(train_id)


@pytest.fixture
def fake_client(train: Train) -> FakeClient:
    client = FakeClient()
    client.set_train(train)
    return client


@pytest.fixture
def http_client(train_id: TrainId) -> HttpClient:
    client = HttpClient()
    client.reset(train_id)
    return client
