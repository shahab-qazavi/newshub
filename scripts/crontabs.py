from crontab import CronTab
import os
print(os.getcwd())
# my_cron = CronTab(user=True)

my_cron = CronTab(user='root')
job = my_cron.new(command='python /home/roy/writeDate.py')
job.minute.every(1)
my_cron.write()
