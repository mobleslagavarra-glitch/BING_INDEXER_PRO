from openpyxl import Workbook

from services.excel_import_service import ExcelImportService


def test_import_excel(monkeypatch, tmp_path):

    file_path = tmp_path / "urls.xlsx"

    workbook = Workbook()
    worksheet = workbook.active

    worksheet.append(["URL"])
    worksheet.append(["https://example.com/uno"])
    worksheet.append(["https://example.com/dos"])
    worksheet.append(["https://example.com/uno"])
    worksheet.append(["https://otro.com/tres"])

    workbook.save(file_path)

    class Domain:
        def __init__(self, id, domain, enabled=True):
            self.id = id
            self.domain = domain
            self.enabled = enabled

    class FakeDomainRepository:

        def get_all(self):
            return [
                Domain(1, "example.com", True)
            ]

    class FakeUrl:

        def __init__(self, url):
            self.url = url

    class FakeUrlRepository:

        def __init__(self):
            self.records = [
                FakeUrl("https://example.com/existente")
            ]
            self.created = []

        def get_all(self):
            return self.records

        def create_many(self, records):
            self.created.extend(records)
            return len(records)

    repository = FakeUrlRepository()

    monkeypatch.setattr(
        "services.excel_import_service.DomainRepository",
        lambda: FakeDomainRepository()
    )

    monkeypatch.setattr(
        "services.excel_import_service.UrlRepository",
        lambda: repository
    )

    service = ExcelImportService()

    result = service.import_file(
        str(file_path)
    )

    assert result["imported"] == 2
    assert result["duplicates"] == 1
    assert result["unknown_domains"] == 1

    assert len(repository.created) == 2

    assert repository.created[0][0] == 1
    assert repository.created[0][2] == "PENDIENTE"


def test_import_excel_requires_url_column(
    tmp_path
):

    file_path = tmp_path / "sin_url.xlsx"

    workbook = Workbook()
    worksheet = workbook.active

    worksheet.append(["Pagina"])
    worksheet.append(["https://example.com/prueba"])

    workbook.save(file_path)

    service = ExcelImportService()

    try:
        service.import_file(
            str(file_path)
        )
        assert False
    except ValueError as error:
        assert "URL" in str(error)


def test_import_excel_invalid_extension(tmp_path):

    file_path = tmp_path / "urls.txt"
    file_path.write_text(
        "https://example.com/prueba",
        encoding="utf-8"
    )

    service = ExcelImportService()

    try:
        service.import_file(
            str(file_path)
        )
        assert False
    except ValueError as error:
        assert ".xlsx" in str(error)

def test_import_excel_empty_file(tmp_path):

    file_path = tmp_path / "vacio.xlsx"

    workbook = Workbook()
    workbook.save(file_path)

    service = ExcelImportService()

    try:
        service.import_file(str(file_path))
        assert False
    except ValueError as error:
        assert "vacío" in str(error).lower()


def test_import_excel_missing_file(tmp_path):

    file_path = tmp_path / "no_existe.xlsx"

    service = ExcelImportService()

    try:
        service.import_file(str(file_path))
        assert False
    except ValueError as error:
        assert "no existe" in str(error).lower()


def test_import_excel_empty_path():

    service = ExcelImportService()

    try:
        service.import_file("")
        assert False
    except ValueError as error:
        assert "seleccionado" in str(error).lower()


def test_import_excel_disabled_domain(
    monkeypatch,
    tmp_path
):

    file_path = tmp_path / "desactivado.xlsx"

    workbook = Workbook()
    worksheet = workbook.active

    worksheet.append(["URL"])
    worksheet.append(["https://example.com/prueba"])

    workbook.save(file_path)

    class Domain:
        def __init__(self):
            self.id = 1
            self.domain = "example.com"
            self.enabled = False

    class FakeDomainRepository:

        def get_all(self):
            return [Domain()]

    class FakeUrlRepository:

        def get_all(self):
            return []

        def create_many(self, records):
            return len(records)

    monkeypatch.setattr(
        "services.excel_import_service.DomainRepository",
        lambda: FakeDomainRepository()
    )

    monkeypatch.setattr(
        "services.excel_import_service.UrlRepository",
        lambda: FakeUrlRepository()
    )

    service = ExcelImportService()

    result = service.import_file(str(file_path))

    assert result["imported"] == 0
    assert result["unknown_domains"] == 1
