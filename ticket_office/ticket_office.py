from client import Client
from reservation import Reservation, TrainId


class TicketOffice:
    def __init__(self, *, client: Client) -> None:
        self.client = client

    def reserve(self, train_id: TrainId, seat_count: int) -> Reservation:
        train = self.client.get_train(train_id)
        to_reserve = []

        for coach in train.coaches():
            occupancy_for_coach_after_booking = train.occupancy_for_coach_after_booking(
                coach, seat_count
            )
            if occupancy_for_coach_after_booking <= 0.7:
                available_seats = [s for s in train.seats_in_coach(coach) if s.is_free]
                to_reserve = available_seats[0:seat_count]
                break

        # TODO: to_reserve may be empty!

        booking_reference = self.client.get_booking_reference()

        seat_ids = [s.id for s in to_reserve]
        reservation = Reservation(
            train=train_id, seats=seat_ids, booking_reference=booking_reference
        )

        self.client.make_reservation(reservation)

        return reservation
