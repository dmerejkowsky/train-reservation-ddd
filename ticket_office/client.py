import abc

from reservation import BookingReference, Reservation, Train, TrainId


class Client(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_train(self, train_id: TrainId) -> Train:
        pass

    @abc.abstractmethod
    def get_booking_reference(self) -> BookingReference:
        pass

    @abc.abstractmethod
    def make_reservation(self, reservation: Reservation) -> None:
        pass
