from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QListWidget,
)

from gui.menu_bar import MainMenu


def get_qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def create_window():
    window = QMainWindow()

    window.stack = QStackedWidget()
    window.navigation = QListWidget()

    for _ in range(6):
        window.stack.addWidget(QListWidget())
        window.navigation.addItem(str(_))

    return window


def get_menu_actions(window):
    return window.menuBar().actions()


def get_menu_action(window, name):
    for action in get_menu_actions(window):
        if action.text() == name:
            return action

    raise AssertionError(f"No se encontró el menú: {name}")


def test_main_menu_creates_all_menus():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    actions = get_menu_actions(window)

    assert [action.text() for action in actions] == [
        "Archivo",
        "Dominios",
        "URLs",
        "IndexNow",
        "Herramientas",
        "Ayuda",
    ]

    assert menu is not None


def test_main_menu_archivo():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    action = get_menu_action(window, "Archivo")

    assert action.text() == "Archivo"
    assert action.menu() is not None
    assert action.menu().actions()[0].text() == "Salir"

    assert menu is not None


def test_main_menu_dominios():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    action = get_menu_action(window, "Dominios")

    assert action.text() == "Dominios"
    assert action.menu() is not None
    assert action.menu().actions()[0].text() == "Gestionar dominios"

    assert menu is not None


def test_main_menu_urls():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    action = get_menu_action(window, "URLs")

    assert action.text() == "URLs"
    assert action.menu() is not None
    assert action.menu().actions()[0].text() == "Gestionar URLs"

    assert menu is not None


def test_main_menu_indexnow():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    action = get_menu_action(window, "IndexNow")

    assert action.text() == "IndexNow"
    assert action.menu() is not None
    assert action.menu().actions()[0].text() == "Enviar a IndexNow"

    assert menu is not None


def test_main_menu_herramientas():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    action = get_menu_action(window, "Herramientas")

    assert action.text() == "Herramientas"
    assert action.menu() is not None

    assert [
        item.text()
        for item in action.menu().actions()
    ] == [
        "Dashboard",
        "Historial",
        "Configuración",
    ]

    assert menu is not None


def test_main_menu_ayuda():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    action = get_menu_action(window, "Ayuda")

    assert action.text() == "Ayuda"
    assert action.menu() is not None
    assert action.menu().actions()[0].text() == "Acerca de"

    assert menu is not None


def test_main_menu_go_to():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    menu.go_to(3)

    assert window.stack.currentIndex() == 3
    assert window.navigation.currentRow() == 3

    menu.go_to(5)

    assert window.stack.currentIndex() == 5
    assert window.navigation.currentRow() == 5


def test_main_menu_navigation_actions():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    dominios = get_menu_action(window, "Dominios")
    urls = get_menu_action(window, "URLs")
    indexnow = get_menu_action(window, "IndexNow")
    herramientas = get_menu_action(window, "Herramientas")

    dominios.menu().actions()[0].trigger()

    assert window.stack.currentIndex() == 1
    assert window.navigation.currentRow() == 1

    urls.menu().actions()[0].trigger()

    assert window.stack.currentIndex() == 2
    assert window.navigation.currentRow() == 2

    indexnow.menu().actions()[0].trigger()

    assert window.stack.currentIndex() == 3
    assert window.navigation.currentRow() == 3

    herramientas.menu().actions()[0].trigger()

    assert window.stack.currentIndex() == 0
    assert window.navigation.currentRow() == 0

    herramientas.menu().actions()[1].trigger()

    assert window.stack.currentIndex() == 4
    assert window.navigation.currentRow() == 4

    herramientas.menu().actions()[2].trigger()

    assert window.stack.currentIndex() == 5
    assert window.navigation.currentRow() == 5

    assert menu is not None


def test_main_menu_show_about():
    get_qapplication()

    window = create_window()
    menu = MainMenu(window)

    from gui import menu_bar

    original_about = menu_bar.QMessageBox.about
    captured = {}

    def fake_about(parent, title, text):
        captured["parent"] = parent
        captured["title"] = title
        captured["text"] = text

    menu_bar.QMessageBox.about = fake_about

    try:
        menu.show_about()
    finally:
        menu_bar.QMessageBox.about = original_about

    assert captured["parent"] is window
    assert captured["title"] == "Acerca de BING INDEXER PRO"
    assert "Versión:" in captured["text"]
    assert "Autor:" in captured["text"]
    assert "Herramienta de gestión e indexación" in captured["text"]
