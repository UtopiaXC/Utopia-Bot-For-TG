import json
import random
import time

from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    Filters
)

import config
import requests

if config.Token == "":
    print("请先在config.py中输入对应Token后使用")
    exit(1)

SETU, SENTENCE, STOCK_FUNC, STOCK_MINE, STOCK_SEARCH, STOCK_SELECT = range(6)
updater = Updater(token=config.Token, use_context=True)
dispatcher = updater.dispatcher
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57 "
}


# 开始功能
def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="欢迎使用Utopia机器人，请使用/help查看全部指令"
    )


handler = CommandHandler('start', start)
dispatcher.add_handler(handler)


# 指令帮助
def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="/help 查看全部指令\n"
             "/setu 获取一张涩图\n"
             "/sentence 获取一句名言\n"
             "/weibo 获取微博热搜\n"
             "/zhihu 随机获取一条知乎日报\n"
             "/bili 随机获取一条bilibili热榜视频\n"
             "/stock 股票操作\n"
             "/cancel 取消正在执行中的任务"
    )


handler = CommandHandler('help', help)
dispatcher.add_handler(handler)


# 涩图功能
def setu_input(update: Update, _: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("R18", callback_data='R18'),
            InlineKeyboardButton("非R18", callback_data='非R18'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '请选择您需要的是R18还是非R18涩图',
        reply_markup=reply_markup,
    )
    return SETU


def setu(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.delete_message()
    url = ""
    r18 = 0
    if query.data == "R18":
        r18 = 1
    try:
        res = requests.get("https://api.lolicon.app/setu/?r18=" + str(r18) + "&apikey=" + config.setu_Token)
        json_str = json.loads(res.text)
        if json_str['code'] == 401:
            query.bot.send_message(
                chat_id=update.effective_chat.id,
                text="API接口超过调用限制（每令牌每天限制300）或API令牌被封禁"
            )
        url = json_str['data'][0]['url']
        author = json_str['data'][0]['author']
        pid = json_str['data'][0]['pid']
        title = json_str['data'][0]['title']
        is_r = "否"
        if r18 != 0:
            is_r = "是"
        query.bot.send_message(chat_id=update.effective_chat.id,
                               text="图片信息：\n"
                                    "作者：" + str(author)
                                    + "\n图片PID：" + str(pid)
                                    + "\n图片标题：" + str(title)
                                    + "\n是否R18：" + is_r)
        query.bot.send_photo(chat_id=update.effective_chat.id,
                             photo=url)
    except Exception as e:
        query.bot.send_message(
            chat_id=update.effective_chat.id,
            text="服务器错误，错误原因：" + str(e) + "\n请自行访问链接：" + url
        )
    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        '命令结束'
    )
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('setu', setu_input)],
    states={
        SETU: [CallbackQueryHandler(setu, pattern='^(R18|非R18)$')]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(conv_handler)


# 一言

def sentence_input(update: Update, _: CallbackContext) -> int:
    keyboard = [
        [
            InlineKeyboardButton("动画", callback_data='a'),
            InlineKeyboardButton("漫画", callback_data='b'),
            InlineKeyboardButton("游戏", callback_data='c'),
            InlineKeyboardButton("文学", callback_data='d'),
        ],
        [
            InlineKeyboardButton("原创", callback_data='e'),
            InlineKeyboardButton("网络", callback_data='f'),
            InlineKeyboardButton("其他", callback_data='g'),
            InlineKeyboardButton("影视", callback_data='h'),
        ],
        [
            InlineKeyboardButton("诗词", callback_data='i'),
            InlineKeyboardButton("网易云", callback_data='j'),
            InlineKeyboardButton("哲学", callback_data='k'),
            InlineKeyboardButton("抖机灵", callback_data='l'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '请选择类型',
        reply_markup=reply_markup,
    )
    return SENTENCE


def sentence(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.delete_message()
    type = query.data
    types = {
        "a": "动画",
        "b": "漫画",
        "c": "游戏",
        "d": "文学",
        "e": "原创",
        "f": "来自网络",
        "g": "其他",
        "h": "影视",
        "i": "诗词",
        "j": "网易云",
        "k": "哲学",
        "l": "抖机灵"
    }
    type_name = types[query.data]
    try:
        res = requests.get("https://v1.hitokoto.cn?c=" + type)
        json_res = json.loads(res.text)
        s = json_res['hitokoto']
        author = json_res['from_who']
        if author == "null" or author is None:
            author = "匿名"
        query.bot.send_message(chat_id=update.effective_chat.id,
                               text="类型：" + type_name + "\n" + s + "\n作者：" + author)
    except Exception as e:
        query.bot.send_message(
            chat_id=update.effective_chat.id,
            text="服务器错误，错误原因" + str(e)
        )
    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        '命令结束'
    )
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('sentence', sentence_input)],
    states={
        SENTENCE: [CallbackQueryHandler(sentence, pattern='^(a|b|c|d|e|f|g|h|i|j|k|l)$')]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(conv_handler)


# 知乎日报
def zhihu(update, context):
    try:
        res = requests.get("https://news-at.zhihu.com/api/3/stories/latest", headers=header)
        json_str = json.loads(res.text)
        index = random.randint(0, len(json_str["stories"]) - 1)
        title = json_str["stories"][index]["title"]
        url = json_str["stories"][index]["url"]
        localtime = time.asctime(time.localtime(time.time()))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='北京时间:' + localtime + " 知乎日报"
                 + "\n文章标题：" + title
                 + "\n文章链接：" + url)
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="服务器错误，错误原因：" + str(e)
        )


handler = CommandHandler('zhihu', zhihu)
dispatcher.add_handler(handler)


# 微博

def bili(update, context):
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
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='北京时间:' + localtime + "\n哔哩哔哩随机热门第" + index + "："
                 + "\n视频标题：" + title
                 + "\nUP主：" + up
                 + "\nBV号：" + bv
                 + "\n视频链接：" + link)
        context.bot.send_photo(
            chat_id=update.effective_chat.id, photo=pic)
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="服务器错误，错误原因：" + str(e)
        )


handler = CommandHandler('bili', bili)
dispatcher.add_handler(handler)


# BILI热搜
def weibo(update, context):
    try:
        res = requests.get("https://s.weibo.com/top/summary")
        soup = BeautifulSoup(res.text)
        res = ""
        for i in range(len(soup.find_all("td", class_="td-02"))):
            if i == 0:
                res += ("置顶热搜：" + soup.find_all("td", class_="td-02")[i].a.get_text() + '\n')
            else:
                res += ("热搜第" + str(i) + "：" + soup.find_all("td", class_="td-02")[i].a.get_text() + '\n')
        localtime = time.asctime(time.localtime(time.time()))
        res += ('北京时间:' + localtime)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=res)
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="服务器错误，错误原因：" + str(e)
        )


handler = CommandHandler('weibo', weibo)
dispatcher.add_handler(handler)


# 股票
def stock_input(update: Update, _: CallbackContext) -> int:
    keyboard = [
        [
            InlineKeyboardButton("自选", callback_data='自选'),
            InlineKeyboardButton("搜索", callback_data='搜索'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '请选择方法',
        reply_markup=reply_markup,
    )
    return STOCK_FUNC


def stock_func(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.delete_message()
    if query.data == "自选":
        query.bot.send_message(
            chat_id=update.effective_chat.id,
            text="该功能正在开发中"
        )
        return STOCK_MINE
    elif query.data == "搜索":
        query.bot.send_message(
            chat_id=update.effective_chat.id,
            text="请输入搜索词"
        )
        return STOCK_SEARCH


def stock_mine():
    pass


def stock_search(update: Update, _: CallbackContext) -> int:
    try:
        key = update.message.text
        session = requests.session()
        session.get("https://xueqiu.com/k?q=" + key, headers=header)
        res = session.get("https://xueqiu.com/query/v1/search/web/stock.json?q=" + key, headers=header)
        json_str = res.json()
        res = json_str['list']
        flag = 0
        keyboard = []
        for i in res:
            flag += 1
            if flag > 5:
                break
            describe = i['name'] + "（股票代码" + i['code'] + "）"
            keyboard.append([InlineKeyboardButton(describe, callback_data=i['code'])])
        if json_str['count'] == 0:
            update.message.reply_text(
                text="无搜索结果"
            )
            return ConversationHandler.END
        text = "获取到的结果共%s个\n请选择一个进行查看\n" % json_str['count']
        if json_str['count'] > 5:
            text += "搜索结果过多，仅显示前五条结果"
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
        )
    except Exception as e:
        update.message.reply_text(
            text="服务器错误，错误原因：" + str(e)
        )
    return STOCK_SELECT


def stock_select(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.delete_message()
    code = query.data

    try:
        session = requests.session()
        session.get("https://xueqiu.com/k?q=" + code, headers=header)
        res = session.get("https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol=" + code, headers=header)
        json_str = res.json()
        # 地区
        region = json_str['data']['items'][0]['market']['region']
        # 交易状态
        status = json_str['data']['items'][0]['market']['status']
        # 时区
        time_zone = json_str['data']['items'][0]['market']['time_zone']
        # 交易市场
        exchange = json_str['data']['items'][0]['quote']['exchange']
        # 货币种类
        currency = json_str['data']['items'][0]['quote']['currency']
        # 股票名
        name = json_str['data']['items'][0]['quote']['name']
        # 数据时间
        dt = json_str['data']['items'][0]['quote']['time']
        if dt is not None:
            time_local = time.localtime(dt / 1000)
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        # 现价
        current = json_str['data']['items'][0]['quote']['current']
        # 今开
        start_price = json_str['data']['items'][0]['quote']['open']
        # 昨收
        end_price = json_str['data']['items'][0]['quote']['last_close']
        # 跌涨数
        cost = 0
        if current is not None and end_price is not None:
            cost = current - end_price
        # 跌涨率%
        rate = 0
        if cost != None and end_price is not None and cost != 0:
            rate = cost / end_price

        cost = float(format(cost, ".2f"))
        if cost > 0:
            cost = "+" + str(cost)
        rate = float(format(rate * 100, ".2f"))
        if rate > 0:
            rate = "+" + str(rate)
        # 最高
        high = json_str['data']['items'][0]['quote']['high']
        # 最低
        low = json_str['data']['items'][0]['quote']['low']
        # 成交量（万手）
        deal = json_str['data']['items'][0]['quote']['volume']
        if deal is not None:
            deal = format(float(format(deal / 10000, ".2f")), ",")
        # 成交额（万元）
        amount = json_str['data']['items'][0]['quote']['amount']
        if amount is not None:
            amount = format(int(format(amount / 10000, ".0f")), ",")
        # 换手
        turnover_rate = json_str['data']['items'][0]['quote']['turnover_rate']
        # 振幅
        amplitude = json_str['data']['items'][0]['quote']['amplitude']
        # 市值（万元）
        total_price = json_str['data']['items'][0]['quote']['market_capital']
        if total_price is not None:
            total_price = format(int(format(total_price / 10000, ".0f")), ",")
        # 总股本（万元）
        total_shares = json_str['data']['items'][0]['quote']['total_shares']
        if total_price is not None:
            total_shares = format(int(format(total_shares / 10000, ".0f")), ",")
        text = "股票名称：%s\n" % name
        text += "股票代码：%s\n" % code
        text += "地区：%s\n" % region
        text += "时区：%s\n" % time_zone
        text += "交易市场：%s\n" % exchange
        text += "货币种类：%s\n" % currency
        text += "交易状态：%s\n" % status
        text += "数据时间（当地）：%s\n" % dt
        text += "现价：%s\n" % current
        text += "今开：%s\n" % start_price
        text += "昨收：%s\n" % end_price
        text += "跌涨：%s\n" % cost
        text += "跌涨率：%s%%\n" % rate
        text += "最高：%s\n" % high
        text += "最低：%s\n" % low
        text += "成交量：%s万手\n" % deal
        text += "成交额：%s万\n" % amount
        text += "换手：%s%%\n" % turnover_rate
        text += "振幅：%s%%\n" % amplitude
        text += "市值：%s万\n" % total_price
        text += "总股本：%s万" % total_shares
        query.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )
    except Exception as e:
        query.bot.send_message(
            chat_id=update.effective_chat.id,
            text="服务器错误，错误原因：" + str(e)
        )
    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        '命令结束'
    )
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('stock', stock_input)],
    states={
        STOCK_FUNC: [CallbackQueryHandler(stock_func, pattern='^(自选|搜索)$')],
        STOCK_SEARCH: [MessageHandler(Filters.text, stock_search)],
        STOCK_MINE: [],
        STOCK_SELECT: [CallbackQueryHandler(stock_select)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(conv_handler)
updater.start_polling()
