import os
import shutil
from datetime import datetime

timformat='%Y-%m-%d %H:%M:%S.%f'
tim=datetime.now().strftime(timformat)
os.chdir('/home/sultana1')
fildername=os.getcwd()
with open("date.txt","a") as f:
    f.write(tim)
    
    f.write("\n")
f.close()
a = tim
counter = 0
for line in reversed(open("date.txt","r").readlines()):
    print( line.rstrip())
    b = datetime.strptime(a,timformat) - datetime.strptime(line.rstrip(),timformat)
    a = line.rstrip()
    if b.days == 0:
        if b.seconds > 10 and b.seconds < 23:
            print(b.seconds)
            counter=counter+1




print("counter = ",counter)
print('\a')

numlines = sum(1 for line in open('date.txt'))
if numlines>5:
    with open('date.txt','r') as f:
        lines=f.readlines()
        f.close()

    with open('date.txt','w') as f:
        f.write(''.join(lines[1:]))
        f.close()


