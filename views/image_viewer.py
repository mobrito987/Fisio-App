import flet as ft


class ImageViewer:
    def __init__(self, store, page):
        self.store = store
        self._page = page
        self.images = {}
        self.left_selector = ft.Dropdown(label="Imagem à esquerda", on_select=self.show_images)
        self.right_selector = ft.Dropdown(label="Imagem à direita", on_select=self.show_images)
        self.left_image = ft.Column(expand=True)
        self.right_image = ft.Column(expand=True)
        self.status = ft.Text()
        self.control = ft.Column(
            controls=[
                ft.Text("Comparar imagens dos prontuários"),
                ft.Text("Selecione duas imagens anexadas para visualizá-las lado a lado."),
                ft.Row(
                    controls=[self.left_selector, self.right_selector],
                    wrap=True,
                ),
                ft.Button(content="Atualizar imagens", on_click=self.refresh_and_show),
                self.status,
                ft.Row(
                    controls=[self.left_image, self.right_image],
                    spacing=32,
                    wrap=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        self.refresh()

    def refresh_and_show(self, _):
        self.refresh()
        self.show_images(None)
        self._page.update()

    def refresh(self):
        selected_left = self.left_selector.value
        selected_right = self.right_selector.value
        rows = self.store.list_record_images()
        self.images = {str(row["id"]): row for row in rows}
        self.left_selector.options = self._options(rows)
        self.right_selector.options = self._options(rows)
        self.left_selector.value = selected_left if selected_left in self.images else None
        self.right_selector.value = selected_right if selected_right in self.images else None
        self.status.value = "" if rows else "Nenhuma imagem foi anexada aos prontuários."

    def _options(self, rows):
        return [
            ft.DropdownOption(
                key=str(row["id"]),
                text=f"{row['name']} — {row['record_date']} — {row['filename']}",
            )
            for row in rows
        ]

    def show_images(self, _):
        self.left_image.controls = self._image_control(self.left_selector.value, "Imagem à esquerda")
        self.right_image.controls = self._image_control(self.right_selector.value, "Imagem à direita")
        if self.left_selector.value or self.right_selector.value:
            self.status.value = ""
        self._page.update()

    def _image_control(self, image_id, label):
        image = self.images.get(image_id)
        if image is None:
            return [ft.Text(f"{label}: selecione uma imagem.")]
        return [
            ft.Text(f"{label}: {image['name']} — {image['record_date']}"),
            ft.Text(image["filename"]),
            ft.Image(
                src=image["content"],
                width=400,
                height=400,
                fit=ft.BoxFit.CONTAIN,
            ),
        ]
