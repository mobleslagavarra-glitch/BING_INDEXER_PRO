from datetime import datetime

from PySide6.QtWidgets import QApplication

from gui.status_bar import StatusBar


def get_qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_status_bar_initial_message():
    get_qapplication()

    status_bar = StatusBar()

    assert status_bar.currentMessage() == "Sistema preparado"


def test_status_bar_disabled():
    get_qapplication()

    status_bar = StatusBar()

    status_bar.update_automation_status(
        False,
        5
    )

    assert (
        status_bar.currentMessage()
        == "Automatización: DESACTIVADA"
    )


def test_status_bar_enabled_without_last_run():
    get_qapplication()

    status_bar = StatusBar()

    status_bar.update_automation_status(
        True,
        5
    )

    assert (
        status_bar.currentMessage()
        == (
            "Automatización: ACTIVA | "
            "Intervalo: 5 min | "
            "Última ejecución: pendiente | "
            "Procesadas: 0 | "
            "OK: 0 | "
            "Errores: 0"
        )
    )


def test_status_bar_enabled_with_last_run():
    get_qapplication()

    status_bar = StatusBar()

    last_run = datetime(
        2026,
        9,
        4,
        14,
        35,
        42
    )

    status_bar.update_automation_status(
        True,
        2,
        last_run,
        10,
        8,
        2
    )

    assert (
        status_bar.currentMessage()
        == (
            "Automatización: ACTIVA | "
            "Intervalo: 2 min | "
            "Última ejecución: 14:35:42 | "
            "Procesadas: 10 | "
            "OK: 8 | "
            "Errores: 2"
        )
    )


def test_status_bar_updates_message():
    get_qapplication()

    status_bar = StatusBar()

    status_bar.update_automation_status(
        True,
        1
    )

    first_message = status_bar.currentMessage()

    status_bar.update_automation_status(
        False,
        1
    )

    second_message = status_bar.currentMessage()

    assert first_message != second_message
    assert second_message == "Automatización: DESACTIVADA"
