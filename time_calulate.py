from datetime import datetime
s2 = '05:46:59.263'
s1 = '05:19:55.353'

FMT = '%H:%M:%S.%f'
tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
print(tdelta)