# -*- coding: utf-8 -*-

import datetime
import dateparser  # https://dateparser.readthedocs.io/en/latest/

from django.shortcuts import render
from django.shortcuts import get_list_or_404
from django.views import generic

from .models import RedEvent

MAX_CONTENT_LEN = 200


def _parse_date(_date_text) -> (bool, str):
    # 抽取年月日
    _date_text = _date_text.replace(" ", "")
    _parsed_date = dateparser.parse(_date_text)
    _message = "无法解析日期数据" if _parsed_date is None else ""
    return _parsed_date, _message


def _is_valid_content(_content_text) -> (bool, str):

    # 文本长度的不可以超过最大长度
    if len(_content_text) > MAX_CONTENT_LEN:
        return False, "事件长度过长"
    else:
        return True, ""


def index(request):
    """ 首页 """

    today = datetime.date.today()
    try:
        today_list = RedEvent.objects.get(event_date__day=today.day)
    except RedEvent.DoesNotExist:
        today_list = None

    month_list = list(range(1, 13))
    return render(request, 'on_this_today/index.html',
                  {"month_list": month_list,
                   "today_list": today_list})


def add_new_event(request):
    """ 添加新的红色历史事件 """

    # 从HTML表单获取日期和事件
    try:
        date_text = request.POST.get('date_text')
        content_text = request.POST.get('content_text')
    except KeyError:
        message = "从HTML网页中读取数据是存在错误。"
        return render(request, 'on_this_today/add_new_event.html', {'message': message})

    # 报错：日期或者文本数据为空
    if date_text is None or content_text is None:
        message = "日期数据和文本数据不能为空。"
        return render(request, 'on_this_today/add_new_event.html', {'message': message})

    # 报错：文本数据中存在问题
    is_valid_text, text_message = _is_valid_content(content_text)
    if not is_valid_text:
        message = text_message
        return render(request, 'on_this_today/add_new_event.html', {'message': message})

    # 报错：日期数据中存在问题
    parsed_date, date_message = _parse_date(date_text)
    if parsed_date is None:
        message = date_message
        return render(request, 'on_this_today/add_new_event.html', {'message': message})

    # 把日期数据转义成 YYYY-MM-DD 的格式
    parsed_date.strftime('%Y-%m-%d')

    # 报错：保存日期和事件信息的过程中出错了
    try:
        RedEvent.objects.create(
            event_text=content_text,
            event_date=parsed_date
        )
    except Exception:
        message = "sqlite failed. "
        return render(request, 'on_this_today/add_new_event.html', {'message': message})

    # 跳转到一个处理提交数据的页面
    message = "successful"
    return render(request, 'on_this_today/add_new_event.html', {'message': str(parsed_date) + " " + content_text})


def month_query(request, _month: int):
    """ 历史上的某月 """

    month = dateparser.parse(str(_month).zfill(2), date_formats=["%m"])
    event_list = get_list_or_404(RedEvent, event_date__month=month.month)
    return render(request, "on_this_today/month_query.html", {'event_list': event_list})


def year_query(request, _year: int):
    """ 历史上的某年 """

    year = dateparser.parse(str(_year).zfill(4), date_formats=["%Y"])
    event_list = get_list_or_404(RedEvent, event_date__year=year.year)
    return render(request, "on_this_today/year_query.html", {'event_list': event_list})
