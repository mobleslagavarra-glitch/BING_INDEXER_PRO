import pytest

from services.history_service import HistoryService


class FakeCursor:

    def __init__(self):
        self.lastrowid = 1
        self.rows = []
        self.rowcount = 0

    def execute(self, query, params=None):

        query = query.strip()

        if query.startswith("INSERT INTO history"):

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

            self.rowcount = 1

        elif query.startswith("SELECT"):

            self.rowcount = len(self.rows)

        elif query.startswith("DELETE FROM history"):

            self.rowcount = len(self.rows)
            self.rows.clear()


    def fetchall(self):
        return list(self.rows)


class FakeConnection:

    def __init__(self):
        self.cursor_instance = FakeCursor()

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        pass

    def close(self):
        pass


def create_service(monkeypatch):

    connection = FakeConnection()

    monkeypatch.setattr(
        HistoryService,
        "get_connection",
        lambda self: connection
    )

    return HistoryService(), connection


def test_add_and_get_all(monkeypatch):

    service, connection = create_service(monkeypatch)

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

    service, connection = create_service(monkeypatch)

    result = service.add(
        "TEST",
        "Evento de prueba"
    )

    assert result == 1

    entries = connection.cursor_instance.fetchall()

    assert entries[0][4] == 0
    assert entries[0][5] == 0
    assert entries[0][6] == 0


def test_add_with_zero_counters(monkeypatch):

    service, connection = create_service(monkeypatch)

    service.add(
        "TEST",
        "Evento",
        0,
        0,
        0
    )

    entry = connection.cursor_instance.rows[0]

    assert entry[4] == 0
    assert entry[5] == 0
    assert entry[6] == 0


def test_add_with_custom_counters(monkeypatch):

    service, connection = create_service(monkeypatch)

    service.add(
        "INDEXACION_COMPLETADA",
        "URL enviada correctamente",
        10,
        8,
        2
    )

    entry = connection.cursor_instance.rows[0]

    assert entry[4] == 10
    assert entry[5] == 8
    assert entry[6] == 2


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


def test_add_none_event_type():

    service = HistoryService()

    with pytest.raises(
        ValueError,
        match="El tipo de evento es obligatorio"
    ):
        service.add(
            None,
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


def test_add_none_description():

    service = HistoryService()

    with pytest.raises(
        ValueError,
        match="La descripción es obligatoria"
    ):
        service.add(
            "TEST",
            None
        )


def test_get_all_returns_entries(monkeypatch):

    service, connection = create_service(monkeypatch)

    service.add(
        "EVENTO_1",
        "Primero"
    )

    service.add(
        "EVENTO_2",
        "Segundo",
        2,
        1,
        1
    )

    result = service.get_all()

    assert len(result) == 2
    assert result[0][2] == "EVENTO_1"
    assert result[1][2] == "EVENTO_2"


def test_clear_returns_deleted_count(monkeypatch):

    service, connection = create_service(monkeypatch)

    service.add(
        "EVENTO_1",
        "Primero"
    )

    service.add(
        "EVENTO_2",
        "Segundo"
    )

    result = service.clear()

    assert result == 2
    assert connection.cursor_instance.rows == []


def test_clear_empty_history_returns_zero(monkeypatch):

    service, connection = create_service(monkeypatch)

    result = service.clear()

    assert result == 0
    assert connection.cursor_instance.rows == []


def test_get_all_empty_history_returns_empty_list(monkeypatch):

    service, connection = create_service(monkeypatch)

    result = service.get_all()

    assert result == []


def test_clear_then_get_all_returns_empty_list(monkeypatch):

    service, connection = create_service(monkeypatch)

    service.add(
        "EVENTO_1",
        "Primero"
    )

    service.add(
        "EVENTO_2",
        "Segundo"
    )

    assert service.clear() == 2
    assert service.get_all() == []
