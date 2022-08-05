from client import Client
from reservation import CoachId, Reservation, Train, TrainId


class TicketOffice:
    def __init__(self, *, client: Client) -> None:
        self.client = client

    def reserve(self, train_id: TrainId, seat_count: int) -> Reservation:
        train = self.client.get_train(train_id)
        to_reserve = []

        coach = self.find_best_coach(train, seat_count)
        assert coach  # TODO
        available_seats = [s for s in train.seats_in_coach(coach) if s.is_free]
        to_reserve = available_seats[0:seat_count]

        booking_reference = self.client.get_booking_reference()

        seat_ids = [s.id for s in to_reserve]
        reservation = Reservation(
            train=train_id, seats=seat_ids, booking_reference=booking_reference
        )

        self.client.make_reservation(reservation)

        return reservation

    def find_best_coach(self, train: Train, seat_count: int) -> CoachId | None:
        for coach in train.coaches():
            if train.occupancy_for_coach_after_booking(coach, seat_count) <= 0.7:
                return coach
        return None
