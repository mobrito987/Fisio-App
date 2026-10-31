import flet as ft


class ScheduleView:
    def __init__(self, store, page):
        self.store = store
        self._page = page
        self.patient_id = ft.TextField(label="ID do paciente")
        self.appointment_date = ft.TextField(label="Data (AAAA-MM-DD)")
        self.appointment_time = ft.TextField(label="Horário")
        self.description = ft.TextField(label="Descrição")
        self.status = ft.Text()
        self.appointment_list = ft.Column()
        self.control = ft.Column(
            controls=[
                ft.Text("Agenda"),
                ft.Text("Use o ID exibido na aba Pacientes."),
                self.patient_id,
                self.appointment_date,
                self.appointment_time,
                self.description,
                ft.Button(content="Agendar atendimento", on_click=self.save_appointment),
                self.status,
                ft.Text("Próximos atendimentos"),
                self.appointment_list,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        self.refresh()

    def save_appointment(self, _):
        try:
            patient_id = int(self.patient_id.value)
            if not self.appointment_date.value.strip() or not self.appointment_time.value.strip():
                raise ValueError
            self.store.add_appointment(
                patient_id,
                self.appointment_date.value.strip(),
                self.appointment_time.value.strip(),
                self.description.value.strip(),
            )
            self.appointment_date.value = ""
            self.appointment_time.value = ""
            self.description.value = ""
            self.status.value = "Atendimento agendado."
            self.refresh()
        except ValueError:
            self.status.value = "Informe o ID, a data e o horário."
        self._page.update()

    def refresh(self):
        appointments = self.store.list_appointments()
        self.appointment_list.controls = [
            ft.Text(
                f"{appointment['appointment_date']} às {appointment['appointment_time']} — "
                f"{appointment['name']} | {appointment['description'] or 'Atendimento'}"
            )
            for appointment in appointments
        ] or [ft.Text("Nenhum atendimento agendado.")]
