from PySide6.QtWidgets import QApplication, QMessageBox

from gui.pages.settings import SettingsPage


def get_qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class FakeSettingsService:

    def __init__(
        self,
        auto="1",
        interval="5",
        retries="3",
        initialize_error=None,
        set_error=None,
    ):
        self.values = {
            "indexnow_auto": auto,
            "indexnow_interval": interval,
            "indexnow_retries": retries,
        }
        self.initialize_error = initialize_error
        self.set_error = set_error
        self.initialize_calls = 0
        self.set_calls = []

    def initialize_defaults(self):
        self.initialize_calls += 1
        if self.initialize_error:
            raise self.initialize_error

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value):
        if self.set_error:
            raise self.set_error
        self.set_calls.append((key, value))
        self.values[key] = value


def create_page(monkeypatch, service=None):

    get_qapplication()

    if service is None:
        service = FakeSettingsService()

    monkeypatch.setattr(
        "gui.pages.settings.SettingsService",
        lambda: service
    )

    page = SettingsPage()

    return page, service


def test_settings_page_initial_structure(monkeypatch):

    page, service = create_page(monkeypatch)

    assert page.lbl_app.text().startswith("Aplicación:")
    assert page.lbl_version.text().startswith("Versión:")
    assert page.lbl_author.text().startswith("Autor:")
    assert page.lbl_status.text() == "Estado: Aplicación operativa"

    assert page.chk_auto.text() == "Envío automático a IndexNow"

    assert page.spin_interval.minimum() == 1
    assert page.spin_interval.maximum() == 1440

    assert page.spin_retries.minimum() == 0
    assert page.spin_retries.maximum() == 10

    assert page.btn_save.text() == "💾 Guardar configuración"
    assert page.btn_refresh.text() == "🔄 Actualizar información"


def test_settings_page_loads_enabled_configuration(monkeypatch):

    service = FakeSettingsService(
        auto="1",
        interval="10",
        retries="5",
    )

    page, service = create_page(
        monkeypatch,
        service
    )

    assert service.initialize_calls == 1
    assert page.chk_auto.isChecked() is True
    assert page.spin_interval.value() == 10
    assert page.spin_retries.value() == 5


def test_settings_page_loads_disabled_configuration(monkeypatch):

    service = FakeSettingsService(
        auto="0",
        interval="2",
        retries="0",
    )

    page, service = create_page(
        monkeypatch,
        service
    )

    assert page.chk_auto.isChecked() is False
    assert page.spin_interval.value() == 2
    assert page.spin_retries.value() == 0


def test_settings_page_load_information(monkeypatch):

    service = FakeSettingsService(
        auto="1",
        interval="15",
        retries="7",
    )

    page, service = create_page(
        monkeypatch,
        service
    )

    service.values["indexnow_auto"] = "0"
    service.values["indexnow_interval"] = "30"
    service.values["indexnow_retries"] = "9"

    page.load_information()

    assert service.initialize_calls == 2
    assert page.chk_auto.isChecked() is False
    assert page.spin_interval.value() == 30
    assert page.spin_retries.value() == 9


def test_settings_page_load_error(monkeypatch):

    service = FakeSettingsService(
        initialize_error=RuntimeError("Error de prueba")
    )

    messages = []

    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args, **kwargs: messages.append(args)
    )

    page, service = create_page(
        monkeypatch,
        service
    )

    assert len(messages) == 1
    assert messages[0][1] == "Error"
    assert "Error de prueba" in messages[0][2]


def test_settings_page_save_enabled(monkeypatch):

    service = FakeSettingsService(
        auto="0",
        interval="1",
        retries="3",
    )

    page, service = create_page(
        monkeypatch,
        service
    )

    page.chk_auto.setChecked(True)
    page.spin_interval.setValue(20)
    page.spin_retries.setValue(6)

    messages = []

    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs: messages.append(args)
    )

    page.save_settings()

    assert service.set_calls == [
        ("indexnow_auto", "1"),
        ("indexnow_interval", "20"),
        ("indexnow_retries", "6"),
    ]

    assert service.values["indexnow_auto"] == "1"
    assert service.values["indexnow_interval"] == "20"
    assert service.values["indexnow_retries"] == "6"

    assert len(messages) == 1
    assert messages[0][1] == "Configuración guardada"
    assert (
        messages[0][2]
        == "La configuración se ha guardado correctamente."
    )


def test_settings_page_save_disabled(monkeypatch):

    service = FakeSettingsService(
        auto="1",
        interval="10",
        retries="5",
    )

    page, service = create_page(
        monkeypatch,
        service
    )

    page.chk_auto.setChecked(False)
    page.spin_interval.setValue(3)
    page.spin_retries.setValue(0)

    messages = []

    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs: messages.append(args)
    )

    page.save_settings()

    assert service.set_calls == [
        ("indexnow_auto", "0"),
        ("indexnow_interval", "3"),
        ("indexnow_retries", "0"),
    ]

    assert len(messages) == 1
    assert messages[0][1] == "Configuración guardada"


def test_settings_page_save_emits_signal(monkeypatch):

    service = FakeSettingsService()

    page, service = create_page(
        monkeypatch,
        service
    )

    emitted = []

    page.settings_saved.connect(
        lambda: emitted.append(True)
    )

    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs: None
    )

    page.save_settings()

    assert emitted == [True]


def test_settings_page_save_error(monkeypatch):

    service = FakeSettingsService(
        set_error=RuntimeError("Error de guardado")
    )

    page, service = create_page(
        monkeypatch,
        service
    )

    messages = []

    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args, **kwargs: messages.append(args)
    )

    page.save_settings()

    assert len(messages) == 1
    assert messages[0][1] == "Error"
    assert "Error de guardado" in messages[0][2]
