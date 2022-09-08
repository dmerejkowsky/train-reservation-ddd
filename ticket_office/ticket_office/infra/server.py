import json

import cherrypy

from ticket_office.domain.client import Reservation, TrainId
from ticket_office.domain.ticket_office import TicketOffice
from ticket_office.infra.http_client import HttpClient


class Server:
    def __init__(
        self,
        *,
        ticket_office: TicketOffice,
    ) -> None:
        self.ticket_office = ticket_office

    def reserve(self, train_id: str, seat_count: str) -> str:
        # TODO: 400 error if train_id is not valid, or seat_count is not an int
        reservation = self.ticket_office.reserve(TrainId(train_id), int(seat_count))
        return serialize_reservation(reservation)


def serialize_reservation(reservation: Reservation) -> str:
    seat_ids = [str(s) for s in reservation.seats]
    as_dict = {
        "train_id": str(reservation.train),
        "seats": seat_ids,
        "booking_reference": str(reservation.booking_reference),
    }
    return json.dumps(as_dict)


def main() -> None:
    Server.reserve.exposed = True # type: ignore[attr-defined]
    cherrypy.config.update({"server.socket_port": 8083})
    client = HttpClient()
    ticket_office = TicketOffice(client=client)
    server = Server(ticket_office=ticket_office)
    cherrypy.quickstart(server)

if __name__ == "__main__":
    main()

