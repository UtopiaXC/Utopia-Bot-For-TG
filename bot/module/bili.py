import json
import random
import time

import requests
from telegram.ext import (
    CommandHandler
)
from .utils.logger import info, warning, error


def add_bili_plugin(dispatcher):
    # BILI热搜
    def bili(update, context):
        try:
            try:
                index = str(random.randint(1, 50))
                res = requests.get("https://api.bilibili.com/x/web-interface/popular?ps=1&pn=" + index)
                json_res = json.loads(res.text)
                title = json_res["data"]["list"][0]["title"]
                pic = json_res["data"]["list"][0]["pic"]
                up = json_res["data"]["list"][0]["owner"]["name"]
                link = json_res["data"]["list"][0]["short_link"]
                bv = json_res["data"]["list"][0]["bvid"]
                localtime = time.asctime(time.localtime(time.time()))
                user = update.effective_user.name + "：\n"
                text = user + '北京时间:' + localtime + "\n哔哩哔哩随机热门第" + index + "：" \
                       + "\n视频标题：" + title \
                       + "\nUP主：" + up \
                       + "\nBV号：" + bv \
                       + "\n视频链接：" + link
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text)
                user_id = str(update.effective_user.id)
                user_name = str(update.effective_user.name)
                log_text = user_name + "(" + user_id + ")" + "获取了一条哔哩哔哩热搜，BV号为" + bv+"，封面为"+pic
                info("bili模块：" + log_text)
                context.bot.send_photo(
                    chat_id=update.effective_chat.id, photo=pic)
            except Exception as e:
                user = update.effective_user.name + "：\n"
                text = user + "服务器错误，错误原因：" + str(repr(e))
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text
                )
                user_id = str(update.effective_user.id)
                user_name = str(update.effective_user.name)
                log_text = user_name + "(" + user_id + ")" + "服务器错误，错误原因：" + str(repr(e))
                error("bili模块：" + log_text)
        except:
            error("bili模块：异常")

    handler = CommandHandler('bili', bili)
    dispatcher.add_handler(handler)
