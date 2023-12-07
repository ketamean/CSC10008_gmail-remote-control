import re

pattern = 'abc2'
string = 'abcdefabcab'
result = re.findall(pattern, string)
print(result)