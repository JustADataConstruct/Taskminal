
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

    def add_task(self,task_name:str,task_start:str,task_end:str,task_total:int):
        self.report += f"<b>{task_name}</b><br> {task_start} -> {task_end} <b>({task_total})</b><br>"

    def add_total(self,task_total):
        self.report += f"<br>Total time: <b>{task_total}</b>"

    def close_report(self):
        self.report += """</body>
                     </html>
        """
        with open("report.html","w") as f:
            f.write(self.report)
    

