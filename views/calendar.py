from datetime import date

import flet as ft

from models import calendar_month, month_title


class CalendarView:
    def __init__(self, store, page):
        self.store = store
        self._page = page
        today = date.today()
        self.year = today.year
        self.month = today.month
        self.month_name = ft.Text()
        self.calendar_grid = ft.Column()
        self.control = ft.Column(
            controls=[
                ft.Text("Calendário de atendimentos"),
                ft.Row(
                    controls=[
                        ft.Button(content="Mês anterior", on_click=self.previous_month),
                        self.month_name,
                        ft.Button(content="Próximo mês", on_click=self.next_month),
                    ],
                    wrap=True,
                ),
                ft.Row(
                    controls=[ft.Text(day) for day in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]]
                ),
                self.calendar_grid,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        self.refresh()

    def previous_month(self, _):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.refresh()
        self._page.update()

    def next_month(self, _):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.refresh()
        self._page.update()

    def refresh(self):
        appointments_by_date = {}
        for appointment in self.store.list_appointments():
            appointments_by_date.setdefault(appointment["appointment_date"], []).append(
                f"{appointment['appointment_time']} — {appointment['name']}"
            )

        self.month_name.value = month_title(self.year, self.month)
        rows = []
        for week in calendar_month(self.year, self.month):
            week_controls = []
            for day in week:
                if day is None:
                    week_controls.append(ft.Column(expand=True, controls=[ft.Text("")]))
                    continue
                date_key = f"{self.year:04d}-{self.month:02d}-{day:02d}"
                week_controls.append(
                    ft.Column(
                        expand=True,
                        controls=[
                            ft.Text(str(day)),
                            *[ft.Text(item) for item in appointments_by_date.get(date_key, [])],
                        ],
                    )
                )
            rows.append(ft.Row(controls=week_controls))
        self.calendar_grid.controls = rows
