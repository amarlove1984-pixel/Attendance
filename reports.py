import pandas as pd
from .models import Attendance

def export_excel():
    qs=Attendance.objects.all().values()
    return pd.DataFrame(list(qs))
