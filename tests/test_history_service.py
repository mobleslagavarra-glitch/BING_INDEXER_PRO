import pytest

from services.history_service import HistoryService


class FakeCursor:

    def __init__(self):
        self.lastrowid = 1
        self.rows = []

    def execute(self, query, params=None):

        if query.strip().startswith("INSERT INTO history"):

            self.rows.append(
                (
                    self.lastrowid,
                    "2026-08-26 21:00:00",
                    params[0],
                    params[1],
                    params[2],
                    params[3],
                    params[4]
                )
            )

    def fetchall(self):
        return self.rows


class FakeConnection:

    def __init__(self):
        self.cursor_instance = FakeCursor()

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        pass

    def close(self):
        pass


def test_add_and_get_all(monkeypatch):

    connection = FakeConnection()

    monkeypatch.setattr(
        HistoryService,
        "get_connection",
        lambda self: connection
    )

    service = HistoryService()

    result = service.add(
        "AUTOMATIZACION_EJECUTADA",
        "Ejecución automática de IndexNow",
        5,
        4,
        1
    )

    assert result == 1

    entries = connection.cursor_instance.fetchall()

    assert len(entries) == 1

    entry = entries[0]

    assert entry[0] == 1
    assert entry[2] == "AUTOMATIZACION_EJECUTADA"
    assert entry[3] == "Ejecución automática de IndexNow"
    assert entry[4] == 5
    assert entry[5] == 4
    assert entry[6] == 1


def test_add_uses_default_counters(monkeypatch):

    connection = FakeConnection()

    monkeypatch.setattr(
        HistoryService,
        "get_connection",
        lambda self: connection
    )

    service = HistoryService()

    result = service.add(
        "TEST",
        "Evento de prueba"
    )

    assert result == 1

    entries = connection.cursor_instance.fetchall()

    assert entries[0][4] == 0
    assert entries[0][5] == 0
    assert entries[0][6] == 0


def test_add_requires_event_type():

    service = HistoryService()

    with pytest.raises(
        ValueError,
        match="El tipo de evento es obligatorio"
    ):
        service.add(
            "",
            "Descripción"
        )


def test_add_requires_description():

    service = HistoryService()

    with pytest.raises(
        ValueError,
        match="La descripción es obligatoria"
    ):
        service.add(
            "TEST",
            ""
        )
