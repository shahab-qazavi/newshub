import subprocess


result = subprocess.getstatusoutput(f'ps -ef | grep python3')

file_names = ['text_reader.py']

for item in result[1].split('\n'):
    finally_result = item.split()
    for name in file_names:
        if name in finally_result[-1]:
            subprocess.run(['kill', '-9', finally_result[1]])
