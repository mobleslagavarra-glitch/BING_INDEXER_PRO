from datetime import datetime

from core.database import Database


class HistoryService:

    def __init__(self):

        self.db = Database()

    def add(

        self,

        event_type,

        description

    ):

        self.db.execute(

            """

            INSERT INTO history

            (

                event_date,

                event_type,

                description

            )

            VALUES(?,?,?)

            """,

            (

                datetime.now().isoformat(),

                event_type,

                description

            )

        )