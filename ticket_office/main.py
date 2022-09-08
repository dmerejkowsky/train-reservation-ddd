import cherrypy

from ticket_office.domain.ticket_office import TicketOffice
from ticket_office.infra.http_client import HttpClient
from ticket_office.infra.server import Server


def main() -> None:
    Server.reserve.exposed = True  # type: ignore[attr-defined]
    cherrypy.config.update({"server.socket_port": 8083})
    client = HttpClient()
    ticket_office = TicketOffice(client=client)
    server = Server(ticket_office=ticket_office)
    cherrypy.quickstart(server)


if __name__ == "__main__":
    main()
