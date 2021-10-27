from datetime import datetime


class League:

    def __init__(self, data: dict = None):
        if data == None:
            return

        self.id = data.get('id')
        self.name = self.id

        self.realm = data.get('realm')
        self.description = data.get('description')

        # self.rules: list = None  #	?array of LeagueRule
        self.register_at: datetime = datetime.fromisoformat(data.get('registerAt'))  #	?str	date time (ISO8601)
        self.event: str = data.get('event')  #	?bool	always true if present
        self.url: str = data.get('url')  #	?str	a url link to a Path of Exile forum thread
        self.startAt: datetime = datetime.fromisoformat(data.get('startAt'))  #	?str	date time (ISO8601)
        self.endAt: datetime = datetime.fromisoformat(data.get('endAt'))  #	?str	date time (ISO8601)
        self.timedEvent: bool = data.get('timedEvent')  #	?bool	always true if present
        self.scoreEvent: bool = data.get('scoreEvent')  #	?bool	always true if present
        self.delveEvent: bool = data.get('delveEvent')  #	?bool	always true if present
