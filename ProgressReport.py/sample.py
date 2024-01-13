from time import sleep
from progress_report import ProgressReport

N  = 10

target = ProgressReport(N)

for i in range(N + 2):
    target.print_progress(i, 'text')
    sleep(0.5)

target.print_progress(i, 'text', last=True)