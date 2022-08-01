import json
import httpx


def test_reserve_seats_from_empty_train():
    train_id = "express_2000"

    client = httpx.Client()
    response = client.post("http://127.0.0.1:8081/reset", data={"train_id": train_id})
    response.raise_for_status()

    reservation = client.post(
        "http://127.0.0.1:8083/reserve", data={"train_id": train_id, "seat_count": 4}
    ).json()

    last_booking_reference = client.get(
        "http://127.0.0.1:8082/last_booking_reference"
    ).text

    assert reservation["train_id"] == "express_2000"
    assert len(reservation["seats"]) == 4
    assert reservation["seats"][0] == "1A"
    assert reservation["booking_reference"] == last_booking_reference
