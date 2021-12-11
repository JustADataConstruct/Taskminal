
from datetime import datetime


class Report:
    def __init__(self) -> None:
        self.report = """<html>
        <head>
        <title>Taskminal Monthly Report</title>
        <h1>Taskminal Monthly Report</h1>
        </head>
        <body>"""

    def add_month(self,month_name:str):
        self.report += f"<h2>{month_name}</h2><br>"

    def add_task(self,task_name:str,task_start:datetime,task_end:datetime,task_total:int):
        start = f"{task_start.month}-{task_start.day}-{task_start.year}, {task_start.hour}:{task_start.minute}:{task_start.second}"
        end = f"{task_end.month}-{task_end.day}-{task_end.year}, {task_end.hour}:{task_end.minute}:{task_end.second}"
        self.report += f"<p><b>{task_name}</b><br> {start} -> {end} <b>({task_total})</b></p>"

    def add_total(self,task_total):
        self.report += f"<br>Total time: <b>{task_total}</b>"

    def close_report(self):
        self.report += """</body>
                     </html>
        """
        with open("report.html","w") as f:
            f.write(self.report)
    

