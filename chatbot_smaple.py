# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 17:05:18 2018

@author: Galil
"""

#!/usr/bin/python
#-*-coding:utf-8 -*
import os
from flask import Flask,url_for,request
from urllib.parse import parse_qs
from chatbot_object import *

app = Flask(__name__)
#起始圖文選單的文字
original_menu = ['sample_1', 'sample_2', 'sample_3', 'about_me']
task_meanu = ['search', 'suggestion']
question_data_path = 'question_data.json'
response_data_path = 'answer_data.json'

test_chatbot = chatbot('1571536404',
                       '2f7228546d598be49bb908b623ff2cd0',
                       question_data_path,
                       response_data_path)


@app.route('/')
def hello_world():
    msg = "機械人測試中 版本:v0.1"
    return msg

@app.route('/callback',methods=["POST"])
def callback():
    temp = request.get_json()
    print(temp)
    for i in temp['events']:
	  #取得回覆token,一個回覆只能用一次		
        reply_token =  i['replyToken']
        #取得uid 
        uid = i['source']['userId']
        if i['type']=='postback': #判斷的參數是哪個
            post=parse_qs(i['postback']['data'])
            """訊息傳送一率是使用postback
               data裡的message_type有兩種值,用以表示tag的類型
               1.question:問題類型,代表其tag是某組問題的關鍵字
               2.answer:答案類型,代表其tag是某組答案的關鍵字
			   3.end_of_return:代表某項任務的結束"""
            if post['message_type'][0] == 'question':
                tag = post['tag'][0]
                for key_word, reply_msg in test_chatbot.template_data.items():
                    if key_word == tag:
                        test_chatbot.line_bot_api.reply_message(reply_token,
                                                                reply_msg)
                        break
            elif post['message_type'][0] == 'answer':
                tag = post['tag'][0]
                for key_word, reply_msg in test_chatbot.response_data.items():
                    if key_word == tag:
                        test_chatbot.line_bot_api.reply_message(reply_token,
                                                                reply_msg)
                        break
            elif post['message_type'][0] == 'end_of_return':
                print('回報的訊息:',test_chatbot.user_list[uid]['report_message'])
                del test_chatbot.user_list[uid]
                reply_msg = TextSendMessage(text='感謝您的建議')
                test_chatbot.line_bot_api.reply_message(reply_token,
                                                        reply_msg)
        elif i['message']['type']=='text':
            """判斷使用者是否在某項狀態中 若沒有則依據訊息進行回應
               因為起始的圖文選單訊息都是text 所以設定一組關鍵字
               只要在關鍵字內的文字訊息就對應相關功能或是回應相關訊息"""
            msg = i['message']['text']
            if uid not in test_chatbot.user_list.keys():
                if msg in original_menu:
                    for key_word, reply_msg in test_chatbot.template_data.items():
                        if key_word == msg:
                            test_chatbot.line_bot_api.reply_message(reply_token,
                                                                     reply_msg)
                            break
                elif msg in task_meanu:
                    task = msg
                    reply_msg = test_chatbot.create_task_template(uid,task)
                    test_chatbot.line_bot_api.reply_message(reply_token,reply_msg)
            #依據不同的任務進行回應
            #problem_return_and_advice
            elif uid in test_chatbot.user_list.keys():
                if test_chatbot.user_list[uid]['task'] == 'suggestion':
                    test_chatbot.user_list[uid]['report_message'] += msg
                elif test_chatbot.user_list[uid]['task'] == 'search':
                    del test_chatbot.user_list[uid]
                    tag = msg
                    for key_word, reply_msg in test_chatbot.response_data.items():
                        if key_word == tag:
                            test_chatbot.line_bot_api.reply_message(reply_token,
                                                                    reply_msg)
                            break
            #例外處理的回應            
            else:
                reply_msg = TextSendMessage(text='若要查詢資料請透過功能選單選擇喔~')
                test_chatbot.line_bot_api.reply_message(reply_token,
                                                        reply_msg)
    return ""
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)