# Note: those tests requires the 3 services (train_data, booking_reference and
# ticket_office) to be up and running
#
# They are slow and unreliable - better to test with the domain objects

import httpx


def test_reserve_seats_from_empty_train() -> None:
    """
    Given no reservation at all
    When we reserve 4 seats
    We get 1A to 4A
    """
    train_id = "express_2000"

    client = httpx.Client()
    response = client.post("http://127.0.0.1:8081/reset", data={"train_id": train_id})
    response.raise_for_status()

    response = client.post(
        "http://127.0.0.1:8083/reserve", data={"train_id": train_id, "seat_count": 4}
    )

    last_booking_reference = client.get(
        "http://127.0.0.1:8082/last_booking_reference"
    ).text

    response.raise_for_status()
    reservation = response.json()
    assert reservation["train_id"] == "express_2000"
    assert len(reservation["seats"]) == 4
    assert reservation["seats"] == ["1A", "2A", "3A", "4A"]
    assert reservation["booking_reference"] == last_booking_reference


def test_reserve_four_additional_seats() -> None:
    """
    Given 4 seats already booked
    When we reserve 4 seats
    We get 5A to 8A
    """
    train_id = "express_2000"
    client = httpx.Client()
    response = client.post("http://127.0.0.1:8081/reset", data={"train_id": train_id})
    response.raise_for_status()
    response = client.post(
        "http://127.0.0.1:8083/reserve", data={"train_id": train_id, "seat_count": 4}
    )
    response.raise_for_status()

    response = client.post(
        "http://127.0.0.1:8083/reserve", data={"train_id": train_id, "seat_count": 4}
    )
    response.raise_for_status()
    reservation = response.json()

    last_booking_reference = client.get(
        "http://127.0.0.1:8082/last_booking_reference"
    ).text
    assert reservation["train_id"] == "express_2000"
    assert len(reservation["seats"]) == 4
    assert reservation["seats"] == ["5A", "6A", "7A", "8A"]
    assert reservation["booking_reference"] == last_booking_reference
