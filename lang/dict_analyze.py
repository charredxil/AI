import re
print("Proper words (1+):  ", len([*re.compile(r'^(?=[a-z]*[aeiouyw][a-z]*$)(?=.{2,}|a$).*', re.M).finditer(open("docs/wordss.txt").read())]))
print("Proper words (3+):  ", len([*re.compile(r'^(?=[a-z]*[aeiouyw][a-z]*$).{3,}', re.M).finditer(open("docs/wordss.txt").read())]))
print("Proper words (4+):  ", len([*re.compile(r'^(?=[a-z]*[aeiouyw][a-z]*$).{4,}', re.M).finditer(open("docs/wordss.txt").read())]))
print("Unique prefixes (3):", len(set(re.compile(r'^(?=[a-z]*[aeiouyw][a-z]*$).{3}', re.M).findall(open("docs/wordss.txt").read()))))
print("Unique prefixes (4):", len(set(re.compile(r'^(?=[a-z]*[aeiouyw][a-z]*$).{4}', re.M).findall(open("docs/wordss.txt").read()))))
