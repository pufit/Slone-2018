# -*- coding: utf-8 -*-
import requests
import json

num = input()

data = {'mod': 'bill.propis', 'q[num]': num}
r = requests.post('https://выставить-счет.рф/number-propis/', data=data)
print(json.loads(r.text)['propis'])
