from PySide6.QtWidgets import QApplication

from gui.navigation import Navigation


def get_qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_navigation_items():
    get_qapplication()

    navigation = Navigation()

    assert navigation.count() == 6

    assert navigation.item(0).text() == "📊 Dashboard"
    assert navigation.item(1).text() == "🌐 Dominios"
    assert navigation.item(2).text() == "🔗 URLs"
    assert navigation.item(3).text() == "📤 IndexNow"
    assert navigation.item(4).text() == "📄 Historial"
    assert navigation.item(5).text() == "⚙️ Configuración"


def test_navigation_maximum_width():
    get_qapplication()

    navigation = Navigation()

    assert navigation.maximumWidth() == 220


def test_navigation_selection():
    get_qapplication()

    navigation = Navigation()

    navigation.setCurrentRow(0)
    assert navigation.currentRow() == 0

    navigation.setCurrentRow(3)
    assert navigation.currentRow() == 3

    navigation.setCurrentRow(5)
    assert navigation.currentRow() == 5
