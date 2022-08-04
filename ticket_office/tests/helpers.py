from client import BookingReference, Client, Reservation, Train, TrainId


class FakeClient(Client):
    def __init__(self) -> None:
        self.train: Train | None = None
        self._booking_reference: BookingReference | None = None

    def set_booking_reference(self, booking_reference: BookingReference) -> None:
        self._booking_reference = booking_reference

    def set_train(self, train: Train) -> None:
        self.train = train

    def get_train(self, train_id: TrainId) -> Train:
        assert self.train
        return self.train

    def make_reservation(self, reservation: Reservation) -> None:
        assert self.train
        for seat_id in reservation.seats:
            existing_reference = self.train.booking_reference(seat_id)
            if (
                existing_reference
                and existing_reference != reservation.booking_reference
            ):
                raise Exception(
                    f"Seat {seat_id} already booked with reference '{existing_reference}'"
                )

    def get_booking_reference(self) -> BookingReference:
        assert self._booking_reference
        return self._booking_reference
