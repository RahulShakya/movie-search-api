import json2xml
from json2xml.utils import readfromurl, readfromstring, readfromjson

data = readfromstring('{"my_items":[{"my_item":{"id":1} },{"my_item":{"id":2} }],"my_str_items":["a","b"]}')
print(json2xml.json2xml(data, item_wrap=False).to_xml())