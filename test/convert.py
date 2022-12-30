import json
from urllib import parse

from srt2bcc import BccConvert

path = "../test/3.srt"
bcc = BccConvert(path).srt2bcc()
# print(bcc)
# print(bcc)
with open("../test/test_3.json", "w", encoding="utf-8") as f:
    json.dump(bcc, f, ensure_ascii=False)
    # data = parse.urlencode({"data":json.dumps(bcc)})
    # f.write(data)
