import flet as ft

from models import create_record_pdf


class RecordView:
    def __init__(self, store, page, file_picker):
        self.store = store
        self._page = page
        self.file_picker = file_picker
        self.pending_attachments = []
        self.patient_id = ft.TextField(label="ID do paciente")
        self.record_date = ft.TextField(label="Data do registro")
        self.content = ft.TextField(label="Evolução / prontuário", multiline=True, min_lines=5)
        self.attachment_status = ft.Text("Nenhum anexo selecionado.")
        self.status = ft.Text()
        self.record_list = ft.Column()
        self.control = ft.Column(
            controls=[
                ft.Text("Prontuário"),
                ft.Text("Anexe imagens, exames ou outros arquivos ao registro."),
                self.patient_id,
                self.record_date,
                self.content,
                ft.Row(
                    controls=[
                        ft.Button(content="Anexar arquivos", icon=ft.Icons.ATTACH_FILE, on_click=self.pick_files),
                        ft.Button(content="Exportar PDF", icon=ft.Icons.PICTURE_AS_PDF, on_click=self.export_pdf),
                    ],
                    wrap=True,
                ),
                self.attachment_status,
                ft.Button(content="Salvar prontuário", on_click=self.save_record),
                self.status,
                ft.Text("Registros salvos"),
                self.record_list,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        self.refresh()

    async def pick_files(self, _):
        files = await self.file_picker.pick_files(allow_multiple=True, with_data=True)
        self.pending_attachments = [
            (selected_file.name, selected_file.bytes)
            for selected_file in files
            if selected_file.bytes is not None
        ]
        names = ", ".join(filename for filename, _ in self.pending_attachments)
        self.attachment_status.value = names or "Nenhum anexo selecionado."
        self._page.update()

    async def export_pdf(self, _):
        try:
            patient_id = int(self.patient_id.value)
            if not self.content.value.strip():
                raise ValueError
            import tempfile
            from pathlib import Path

            temporary_path = Path(tempfile.gettempdir()) / "prontuario_fisioapp.pdf"
            create_record_pdf(
                temporary_path,
                patient_id,
                self.record_date.value.strip(),
                self.content.value.strip(),
            )
            await self.file_picker.save_file(
                dialog_title="Salvar prontuário em PDF",
                file_name="prontuario.pdf",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
                src_bytes=temporary_path.read_bytes(),
            )
            self.status.value = "PDF preparado para salvar."
        except ValueError:
            self.status.value = "Informe o ID do paciente e o conteúdo do prontuário."
        self._page.update()

    def save_record(self, _):
        try:
            patient_id = int(self.patient_id.value)
            if not self.content.value.strip():
                raise ValueError
            self.store.add_record(
                patient_id,
                self.record_date.value.strip(),
                self.content.value.strip(),
                self.pending_attachments,
            )
            self.content.value = ""
            self.pending_attachments = []
            self.attachment_status.value = "Nenhum anexo selecionado."
            self.status.value = "Prontuário salvo."
            self.refresh()
        except ValueError:
            self.status.value = "Informe o ID do paciente e o conteúdo do prontuário."
        self._page.update()

    def refresh(self):
        records = self.store.list_records()
        self.record_list.controls = [
            ft.Text(
                f"{record['record_date'] or 'Sem data'} — {record['name']} — "
                f"{record['attachment_count']} anexo(s)"
            )
            for record in records
        ] or [ft.Text("Nenhum prontuário salvo.")]
