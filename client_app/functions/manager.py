from crontab import CronTab
import subprocess

planed_commands: list[str] = subprocess.check_output("crontab -l", shell=True).decode().split('\n')
job_commands: list[str] = []

for command_string in planed_commands:
    comment = command_string.split('#')[1].strip()
    if "farm" in comment:
        job_commands.append(command_string)




