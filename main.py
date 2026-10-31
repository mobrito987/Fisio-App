import flet as ft

from models import ClinicStore
from views.calendar import CalendarView
from views.evaluation import EvaluationView
from views.image_viewer import ImageViewer
from views.patients import PatientsView
from views.record import RecordView
from views.schedule import ScheduleView


async def main(page: ft.Page):
    page.title = "FisioApp"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.LIGHT_BLUE_50
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.LIGHT_BLUE)

    store = ClinicStore()
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    patients_view = PatientsView(store, page)
    calendar_view = CalendarView(store, page)
    evaluation_view = EvaluationView(store, page)
    record_view = RecordView(store, page, file_picker)
    image_viewer = ImageViewer(store, page)
    schedule_view = ScheduleView(store, page)

    def refresh_views(_):
        calendar_view.refresh()
        image_viewer.refresh()
        page.update()

    page.add(
        ft.Tabs(
            length=6,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        on_click=refresh_views,
                        tabs=[
                            ft.Tab(label="Pacientes"),
                            ft.Tab(label="Calendário"),
                            ft.Tab(label="Avaliação"),
                            ft.Tab(label="Prontuário"),
                            ft.Tab(label="Imagens"),
                            ft.Tab(label="Agenda"),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            patients_view.control,
                            calendar_view.control,
                            evaluation_view.control,
                            record_view.control,
                            image_viewer.control,
                            schedule_view.control,
                        ],
                    ),
                ],
            ),
        )
    )


ft.run(main)
