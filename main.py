import sys
import re
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QFormLayout,
)
from crontab import CronTab


class CronManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cron = CronTab(user=True)

    def initUI(self):
        self.setWindowTitle("Менеджер Cron задач")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.list_jobs_btn = QPushButton("Список задач")
        self.list_jobs_btn.clicked.connect(self.list_jobs)
        layout.addWidget(self.list_jobs_btn)

        self.jobs_display = QTextEdit()
        self.jobs_display.setReadOnly(True)
        layout.addWidget(self.jobs_display)

        form_layout = QFormLayout()

        self.command_input = QLineEdit()
        self.schedule_input = QLineEdit()
        self.comment_input = QLineEdit()

        form_layout.addRow("Команда:", self.command_input)
        form_layout.addRow("Расписание:", self.schedule_input)
        form_layout.addRow("Название:", self.comment_input)

        self.add_job_btn = QPushButton("Добавить задачу")
        self.add_job_btn.clicked.connect(self.add_job)
        form_layout.addWidget(self.add_job_btn)

        self.comment_remove_input = QLineEdit()
        form_layout.addRow("Название для удаления:", self.comment_remove_input)

        self.remove_job_btn = QPushButton("Удалить задачу")
        self.remove_job_btn.clicked.connect(self.remove_job)
        form_layout.addWidget(self.remove_job_btn)

        self.comment_modify_input = QLineEdit()
        self.new_command_input = QLineEdit()
        self.new_schedule_input = QLineEdit()

        form_layout.addRow("Название для изменения:", self.comment_modify_input)
        form_layout.addRow("Новая команда:", self.new_command_input)
        form_layout.addRow("Новое расписание:", self.new_schedule_input)

        self.modify_job_btn = QPushButton("Изменить задачу")
        self.modify_job_btn.clicked.connect(self.modify_job)
        form_layout.addWidget(self.modify_job_btn)

        layout.addLayout(form_layout)
        self.setLayout(layout)

    def list_jobs(self):
        self.jobs_display.clear()
        for job in self.cron:
            self.jobs_display.append(
                f"ID задачи: {job.comment}, Команда: {job.command}, Расписание: {job.slices}"
            )

    def add_job(self):
        command = self.command_input.text()
        schedule = self.schedule_input.text()
        comment = self.comment_input.text()

        if command and schedule and comment:
            if self.validate_schedule(schedule):
                try:
                    job = self.cron.new(command=command, comment=comment)
                    job.setall(schedule)
                    self.cron.write()
                    QMessageBox.information(self, "Успех", "Задача успешно добавлена")
                    self.list_jobs()
                except KeyError as e:
                    QMessageBox.critical(
                        self, "Ошибка", f"Не удалось добавить задачу: {e}"
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка ввода",
                    'Неверный формат расписания. Ожидаемый формат: "* * * * *"',
                )
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Все поля должны быть заполнены")

    def remove_job(self):
        comment = self.comment_remove_input.text()
        if comment:
            job = None
            for j in self.cron:
                if j.comment == comment:
                    job = j
                    break
            if job:
                self.cron.remove(job)
                self.cron.write()
                QMessageBox.information(self, "Успех", "Задача успешно удалена")
                self.list_jobs()
            else:
                QMessageBox.warning(
                    self, "Ошибка", f"Задача с ID: {comment} не найдена"
                )
        else:
            QMessageBox.warning(
                self, "Ошибка ввода", "Поле комментария должно быть заполнено"
            )

    def modify_job(self):
        comment = self.comment_modify_input.text()
        new_command = self.new_command_input.text()
        new_schedule = self.new_schedule_input.text()

        if comment:
            job = None
            for j in self.cron:
                if j.comment == comment:
                    job = j
                    break
            if job:
                if new_command:
                    job.set_command(new_command)
                if new_schedule:
                    if self.validate_schedule(new_schedule):
                        job.setall(new_schedule)
                    else:
                        QMessageBox.warning(
                            self,
                            "Ошибка ввода",
                            'Неверный формат расписания. Ожидаемый формат: "* * * * *"',
                        )
                        return
                self.cron.write()
                QMessageBox.information(self, "Успех", "Задача успешно изменена")
                self.list_jobs()
            else:
                QMessageBox.warning(
                    self, "Ошибка", f"Задача с ID: {comment} не найдена"
                )
        else:
            QMessageBox.warning(
                self,
                "Ошибка ввода",
                "Поле комментария для изменения должно быть заполнено",
            )

    def validate_schedule(self, schedule):
        pattern = r"^(\*|[0-5]?\d) (\*|[01]?\d|2[0-3]) (\*|0?[1-9]|[12]\d|3[01]) (\*|0?[1-9]|1[0-2]) (\*|[0-6])$"
        return bool(re.match(pattern, schedule))


def main():
    app = QApplication(sys.argv)
    manager = CronManager()
    manager.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
