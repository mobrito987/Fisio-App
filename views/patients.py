import flet as ft


class PatientsView:
    def __init__(self, store, page):
        self.store = store
        self._page = page
        self.name = ft.TextField(label="Nome")
        self.phone = ft.TextField(label="Telefone")
        self.birth_date = ft.TextField(label="Data de nascimento")
        self.notes = ft.TextField(label="Observações", multiline=True)
        self.status = ft.Text()
        self.patient_list = ft.Column()
        self.control = ft.Column(
            controls=[
                ft.Text("Cadastro de pacientes"),
                self.name,
                self.phone,
                self.birth_date,
                self.notes,
                ft.Button(content="Salvar paciente", on_click=self.save_patient),
                self.status,
                ft.Text("Pacientes cadastrados"),
                self.patient_list,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        self.refresh()

    def save_patient(self, _):
        if not self.name.value.strip():
            self.status.value = "Informe o nome do paciente."
        else:
            self.store.add_patient(
                self.name.value.strip(),
                self.phone.value.strip(),
                self.birth_date.value.strip(),
                self.notes.value.strip(),
            )
            self.name.value = ""
            self.phone.value = ""
            self.birth_date.value = ""
            self.notes.value = ""
            self.status.value = "Paciente salvo."
            self.refresh()
        self._page.update()

    def refresh(self):
        patients = self.store.list_patients()
        self.patient_list.controls = [
            ft.Text(f"#{patient['id']} — {patient['name']} | {patient['phone'] or 'Sem telefone'}")
            for patient in patients
        ] or [ft.Text("Nenhum paciente cadastrado.")]
