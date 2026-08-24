from PySide6.QtWidgets import QStatusBar


class StatusBar(QStatusBar):

    def __init__(self):

        super().__init__()

        self.showMessage("Sistema preparado")

    def update_automation_status(
        self,
        enabled,
        interval_minutes,
        last_run=None,
        processed=0,
        success=0,
        errors=0
    ):

        if not enabled:

            self.showMessage(
                "Automatización: DESACTIVADA"
            )

            return

        if last_run is None:

            ultima = "pendiente"

        else:

            ultima = last_run.strftime(
                "%H:%M:%S"
            )

        self.showMessage(
            f"Automatización: ACTIVA | "
            f"Intervalo: {interval_minutes} min | "
            f"Última ejecución: {ultima} | "
            f"Procesadas: {processed} | "
            f"OK: {success} | "
            f"Errores: {errors}"
        )
