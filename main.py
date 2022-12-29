# -*-coding:utf8-*-
import requests
import json
import time
import os
from datetime import datetime
import codecs
import srt
from pyrogram import Client
from pyrogram import filters

api_id = 123456
api_hash = "abcdefghijklmnopqrstuvwxyz"
bot_token = "114514:QWERTYUIOP-ASDFGHJKL-ZXCVBNM"
lang_code = "zh"
時長 = 5

app = Client(
    "SRT2BCC_bot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token,
    lang_code=lang_code
)

@app.on_message(filters.command(["start","help"]))
async def end(client, message):
    await message.reply_text("向bot私聊发送SRT字幕文件即可将其转换为BCC字幕格式\n注意:若BOT长时间未发送文件 大概率为SRT字幕文件格式错误", quote=True)

@app.on_message(filters.document & filters.private)
async def main(client, message):
    empty_folder("./downloads")
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_size = message.document.file_size
    if file_name.endswith('.srt'):
        if file_size <= 256000:
            await message.download(file_name)
            await message.reply_text("字幕文件转换中……请稍后", quote=True)
            字幕转换()
            file_path = "./bcc/"+file_name.replace(".srt", ".json")
            await message.reply_document(document=file_path)
            empty_folder("./downloads")
            empty_folder("./bcc")
            await message.reply_text("转换完成", quote=True)
        else:
            await message.reply_text("文件过大", quote=True)
    else:
        await message.reply_text("非SRT字幕文件", quote=True)

def empty_folder(filepath):
    del_list = os.listdir(filepath)
    for f in del_list:
        file_path = os.path.join(filepath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

def 字幕转换():
    srtdir = './downloads'
    bccdir = './bcc'
    for fname in os.listdir(srtdir):
        if os.path.splitext(fname)[-1] == ".srt":
            with codecs.open(os.path.join(srtdir, fname), 'r', encoding='utf-8') as f:
                body = []
                body_json = {}
                排序arr = {}
                最大值 = {}
                subtitle_generator = srt.parse(f.read())
                subtitles = list(subtitle_generator)

                for k, v in enumerate(subtitles):
                    start_time = v.start.total_seconds()
                    end_time = v.end.total_seconds()
                    content = v.content
                    if (len(content)== 0): continue
                    if (content[-1]=="\n"):
                        content = content[:-1]
                    替換 = 0
                    for i in list(最大值.keys()):
                        old_start_time = 最大值[i][0]
                        old_end_time = 排序arr[old_start_time][1]
                        old_content = 排序arr[old_start_time][2]
                        if start_time < i:
                            if old_end_time == end_time:
                                替換 = 1
                                if old_start_time < start_time:
                                    排序arr[old_start_time] = [old_start_time,start_time,str(old_content)]
                                    最大值[start_time] = [old_start_time]
                                    排序arr[start_time] = [start_time,end_time,str(content)+"\n"+str(old_content)]
                                    最大值[end_time] = [start_time]
                                elif old_start_time > start_time:
                                    排序arr[start_time] = [start_time,old_start_time,str(content)]
                                    最大值[old_start_time] = [start_time]
                                    end_time = old_start_time
                                    排序arr[old_start_time] = [old_start_time,end_time,str(old_content)+"\n"+str(content)]
                                    最大值[end_time] = [old_start_time]
                                else:
                                    排序arr[start_time] = [start_time,end_time,str(content)+"\n"+str(old_content)]
                                    最大值[end_time] = [start_time]
                            elif old_start_time == start_time:
                                替換 = 1
                                if (old_end_time < end_time):                                            
                                    排序arr[start_time] = [start_time,old_end_time,str(old_content)+"\n"+str(content)]
                                    最大值[old_end_time] = [start_time]
                                    排序arr[old_end_time] = [old_end_time,end_time,str(content)]
                                    end_time = old_end_time
                                    最大值[end_time] = [old_end_time]
                                elif (old_end_time > end_time):
                                    排序arr[start_time] = [start_time,end_time,str(content)+"\n"+str(old_content)]
                                    最大值[end_time] = [start_time]
                                    排序arr[end_time] = [end_time,old_end_time,str(old_content)]
                                    最大值[old_end_time] = [end_time]
                        elif start_time == i:
                            if (old_end_time == end_time):
                                替換 = 1
                                排序arr[start_time] = [start_time,end_time,str(content)+"\n"+str(old_content)]
                                最大值[end_time] = [start_time]
                    if 替換 == 0:
                        排序arr[start_time] = [start_time,end_time,str(content)]
                        最大值[end_time] = [start_time]

                總表 = {}
                反查表 = {}
                時間表 = []
                in表 = []
                out表 = []
                for myarr in 排序arr:
                    body_json = {}
                    body_json["from"] = 排序arr[myarr][0]
                    body_json["to"] = 排序arr[myarr][1]
                    body_json["content"] = 排序arr[myarr][2]
                    總表[排序arr[myarr][0]] = body_json
                    反查表[排序arr[myarr][1]] = 排序arr[myarr][0]
                    時間表.append(排序arr[myarr][0])
                    in表.append(排序arr[myarr][0])
                    時間表.append(排序arr[myarr][1])
                    out表.append(排序arr[myarr][1])
                
                內容 = {}
                body_json = {}
                start = 0
                From = 0
                To = 0
                for i in sorted(set(時間表)):
                    if i in out表:
                        From = To
                        To = i
                        del 內容[反查表[i]]
                        if start == 1:
                            body_json["from"] = From
                            body_json["to"] = To
                            body_json["location"] = 2
                            body_json["content"] = 新內容
                            body.append(body_json)
                            body_json = {}
                        新內容 = ""
                        for ii in 內容.values():
                            if 新內容 == "":
                                新內容 = ii
                            else:
                                新內容 = ii+"\n"+新內容
                        if 新內容 == "":
                            start = 0
                        else:
                            start = 1
                    if i in in表:
                        From = To
                        To = i
                        if start == 1:
                            body_json["from"] = From
                            body_json["to"] = To
                            body_json["location"] = 2
                            body_json["content"] = 新內容
                            body.append(body_json)
                            body_json = {}
                        內容[i] = 總表[i]["content"]
                        新內容 = ""
                        for ii in 內容.values():
                            if 新內容 == "":
                                新內容 = ii
                            else:
                                新內容 = ii+"\n"+新內容
                        if 新內容 == "":
                            start = 0
                        else:
                            start = 1
                bcc = {"body": body}
                name, _ = os.path.splitext(fname)
                bccname = name + '.json'
                with codecs.open(os.path.join(bccdir, bccname), 'w', encoding='utf-8') as f:
                    json.dump(bcc, f, ensure_ascii=False)
            寫入字幕(bccdir,bccname)

def 寫入字幕(fpath,fname):
    global 時長
    if fname.find("cht") != -1:
        info = "「字幕由 富睿字幕組 搬運」\n（禁止在B站宣傳漫遊相關内容，否則拉黑）"
    elif fname.find(".tc") != -1:
        info = "「字幕由 富睿字幕組 搬運」\n（禁止在B站宣傳漫遊相關内容，否則拉黑）"
    elif fname.find(".tw") != -1:
        info = "「字幕由 富睿字幕組 搬運」\n（禁止在B站宣傳漫遊相關内容，否則拉黑）"
    else:
        info = "「字幕由 富睿字幕组 搬运」\n（禁止在B站宣传漫游相关内容，否则拉黑）"
    插入內容 = {}
    插入內容['content'] = info
    插入內容['location'] = 2
    插入內容['from'] = 0
    bodys = {}
    with open(os.path.join(fpath, fname), 'r', encoding='utf-8') as f:
        response = f.read()
    try:
        jsons = json.loads(str(response))
        bodys = jsons["body"]
        start = bodys[0]["from"]
        end = bodys[0]["to"]
        content = bodys[0]["content"]
    except:
        start = 時長
    
    if start >= 時長:
        start = 時長
        插入內容['to'] = 時長
        bodys.insert(0,插入內容)
    elif end >= 時長:
        bodys[0]["from"] = 時長
        插入內容2 = {}
        插入內容2['content'] = content+"\n"+info
        插入內容2['location'] = 2
        插入內容2['from'] = start
        插入內容2['to'] = 時長
        bodys.insert(0,插入內容2)
        if start != 0:
            插入內容['to'] = start
            bodys.insert(0,插入內容)
    else:
        bodys[0]["content"] = content+"\n"+info
        for ii in range(1,10):
            if(bodys[ii]["to"] <= 時長):
                bodys[ii]["content"] = bodys[ii]["content"]+"\n"+info
        if start != 0:
            插入內容['to'] = start
            bodys.insert(0,插入內容)
            
    bcc = {"body": bodys}
    content = json.dumps(bcc, ensure_ascii=False).replace('"content": "','"content":"').replace(', "from": ',',"from":').replace(', "to": ',',"to":').replace(', "location": ',',"location":').replace('}, {"cont','},{"cont').replace(': [{"cont',':[{"cont')
    with open(os.path.join(fpath, fname), 'w', encoding='utf-8') as f:
        f.write(content)

app.run()