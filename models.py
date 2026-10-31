import calendar
import sqlite3
import unicodedata
from datetime import date
from pathlib import Path


class ClinicStore:
    def __init__(self, database_path: str = "fisioapp.db"):
        self.database_path = Path(database_path)
        self._create_tables()

    def _connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_tables(self):
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    birth_date TEXT,
                    notes TEXT
                );
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    evaluation_date TEXT,
                    diagnosis TEXT,
                    objective TEXT,
                    FOREIGN KEY(patient_id) REFERENCES patients(id)
                );
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    record_date TEXT,
                    content TEXT NOT NULL,
                    FOREIGN KEY(patient_id) REFERENCES patients(id)
                );
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    content BLOB NOT NULL,
                    FOREIGN KEY(record_id) REFERENCES records(id)
                );
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    appointment_date TEXT NOT NULL,
                    appointment_time TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY(patient_id) REFERENCES patients(id)
                );
                """
            )

    def add_patient(self, name, phone, birth_date, notes):
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO patients (name, phone, birth_date, notes) VALUES (?, ?, ?, ?)",
                (name, phone, birth_date, notes),
            )

    def list_patients(self):
        with self._connection() as connection:
            return connection.execute(
                "SELECT id, name, phone, birth_date FROM patients ORDER BY name"
            ).fetchall()

    def add_evaluation(self, patient_id, evaluation_date, diagnosis, objective):
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO evaluations (patient_id, evaluation_date, diagnosis, objective)
                   VALUES (?, ?, ?, ?)""",
                (patient_id, evaluation_date, diagnosis, objective),
            )

    def add_record(self, patient_id, record_date, content, attachments):
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO records (patient_id, record_date, content) VALUES (?, ?, ?)",
                (patient_id, record_date, content),
            )
            record_id = cursor.lastrowid
            connection.executemany(
                "INSERT INTO attachments (record_id, filename, content) VALUES (?, ?, ?)",
                [(filename, content) for filename, content in attachments],
            )

    def list_records(self):
        with self._connection() as connection:
            return connection.execute(
                """SELECT records.id, patients.name, records.record_date, records.content,
                          COUNT(attachments.id) AS attachment_count
                   FROM records
                   JOIN patients ON patients.id = records.patient_id
                   LEFT JOIN attachments ON attachments.record_id = records.id
                   GROUP BY records.id
                   ORDER BY records.id DESC"""
            ).fetchall()

    def list_record_images(self):
        with self._connection() as connection:
            return connection.execute(
                """SELECT attachments.id, attachments.filename, attachments.content,
                          records.record_date, patients.name
                   FROM attachments
                   JOIN records ON records.id = attachments.record_id
                   JOIN patients ON patients.id = records.patient_id
                   WHERE lower(attachments.filename) LIKE '%.png'
                      OR lower(attachments.filename) LIKE '%.jpg'
                      OR lower(attachments.filename) LIKE '%.jpeg'
                      OR lower(attachments.filename) LIKE '%.gif'
                      OR lower(attachments.filename) LIKE '%.webp'
                   ORDER BY records.record_date DESC, attachments.id DESC"""
            ).fetchall()

    def add_appointment(self, patient_id, appointment_date, appointment_time, description):
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO appointments (patient_id, appointment_date, appointment_time, description)
                   VALUES (?, ?, ?, ?)""",
                (patient_id, appointment_date, appointment_time, description),
            )

    def list_appointments(self):
        with self._connection() as connection:
            return connection.execute(
                """SELECT appointments.id, patients.name, appointments.appointment_date,
                          appointments.appointment_time, appointments.description
                   FROM appointments
                   JOIN patients ON patients.id = appointments.patient_id
                   ORDER BY appointments.appointment_date, appointments.appointment_time"""
            ).fetchall()


def calendar_month(year, month):
    first_weekday, days_in_month = calendar.monthrange(year, month)
    cells = [None] * first_weekday + list(range(1, days_in_month + 1))
    cells.extend([None] * ((7 - len(cells) % 7) % 7))
    return [cells[position : position + 7] for position in range(0, len(cells), 7)]


def month_title(year, month):
    return date(year, month, 1).strftime("%B de %Y").capitalize()


def create_record_pdf(path, patient_id, record_date, content):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    def plain_text(value):
        return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()

    document = canvas.Canvas(path, pagesize=A4)
    _, height = A4
    y_position = height - 56
    document.setFont("Helvetica-Bold", 16)
    document.drawString(48, y_position, "FisioApp - Prontuario")
    y_position -= 30
    document.setFont("Helvetica", 11)
    for line in [f"Paciente ID: {patient_id}", f"Data: {record_date}", "", *content.splitlines()]:
        for wrapped_line in _wrap(plain_text(line), 90):
            if y_position < 56:
                document.showPage()
                document.setFont("Helvetica", 11)
                y_position = height - 56
            document.drawString(48, y_position, wrapped_line)
            y_position -= 16
    document.save()


def _wrap(text, maximum_length):
    if not text:
        return [""]
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        candidate = f"{current_line} {word}".strip()
        if len(candidate) > maximum_length and current_line:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate
    return lines + [current_line]
