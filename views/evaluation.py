import flet as ft


class EvaluationView:
    def __init__(self, store, page):
        self.store = store
        self._page = page
        self.patient_id = ft.TextField(label="ID do paciente")
        self.evaluation_date = ft.TextField(label="Data da avaliação")
        self.diagnosis = ft.TextField(label="Diagnóstico / queixa")
        self.objective = ft.TextField(label="Objetivo terapêutico", multiline=True)
        self.status = ft.Text()
        self.control = ft.Column(
            controls=[
                ft.Text("Avaliação fisioterapêutica"),
                ft.Text("Use o ID exibido na aba Pacientes."),
                self.patient_id,
                self.evaluation_date,
                self.diagnosis,
                self.objective,
                ft.Button(content="Salvar avaliação", on_click=self.save_evaluation),
                self.status,
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def save_evaluation(self, _):
        try:
            patient_id = int(self.patient_id.value)
            if not self.diagnosis.value.strip():
                raise ValueError
            self.store.add_evaluation(
                patient_id,
                self.evaluation_date.value.strip(),
                self.diagnosis.value.strip(),
                self.objective.value.strip(),
            )
            self.status.value = "Avaliação salva."
            self.diagnosis.value = ""
            self.objective.value = ""
        except ValueError:
            self.status.value = "Informe um ID de paciente e o diagnóstico."
        self._page.update()
