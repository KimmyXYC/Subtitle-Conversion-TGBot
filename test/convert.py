import json
from urllib import parse

from subtitle_utils import BccConvert

path = "../test/3.srt"
bcc = BccConvert().srt2bcc(files=path)
# print(bcc)
# print(bcc)
with open("../test/test_3.json", "w", encoding="utf-8") as f:
    json.dump(bcc, f, ensure_ascii=False)
    # data = parse.urlencode({"data":json.dumps(bcc)})
    # f.write(data)
