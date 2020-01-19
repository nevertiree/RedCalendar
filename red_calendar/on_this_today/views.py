# -*- coding: utf-8 -*-

import json
import datetime
import dateparser  # https://dateparser.readthedocs.io/en/latest/

from django.shortcuts import render
from django.shortcuts import get_list_or_404

from .models import RedEvent
from .forms import AddFrom

MAX_CONTENT_LEN = 200


def _parse_date(_date_text) -> (bool, str):
    # 抽取年月日
    _date_text = _date_text.replace(" ", "")
    _date_format = ['%Y-%m-%d',
                    '%Y年%m月%d日',
                    '%Y/%m/%d',
                    ]
    _parsed_date = dateparser.parse(_date_text,
                                    date_formats=_date_format,
                                    settings={'STRICT_PARSING': True})
    _message = "无法解析日期数据" if _parsed_date is None else ""
    return _parsed_date, _message


def _is_valid_content(_content_text) -> (bool, str):

    # 文本长度的不可以超过最大长度
    if len(_content_text) > MAX_CONTENT_LEN:
        return False, "事件长度过长"
    else:
        return True, ""


def _event_obj_2_json(_event_obj_list):
    """
        把事件信息转义成JSON格式
        events: [
            {
                title: '【1870】列宁逝世',
                start: '2020-01-21',
            },
        ]
        :param _event_obj_list:
        :return: json
    """
    result = []

    for _event in _event_obj_list:
        event_date = _event.event_date
        event_year = event_date.year
        event_date = event_date.replace(year=datetime.date.today().year)
        result.append({
            "title": "【" + str(event_year) + "】" + _event.event_text,
            "start": str(event_date)
        })

    return json.dumps(result)


def index(request):
    """ 首页 """

    today = datetime.date.today()  # 获取今天的日期
    try:
        events_in_this_month = RedEvent.objects.filter(event_date__month=today.month)  # 查询这个月的其他事件
    except RedEvent.DoesNotExist:
        events_in_this_month = None

    events_json = _event_obj_2_json(events_in_this_month)  # 把查询结果包装成JSON形式

    return render(request, 'on_this_today/index.html',
                  {"event_in_this_month": events_json})


def add_new_event(request):
    """ 添加新的红色历史事件 """

    # 从HTML表单获取日期和事件
    if request.method == "POST":  # 提交表单时
        form = AddFrom(request.POST)
        try:
            if form.is_valid():
                date_text = form.cleaned_data['date_text']
                content_text = form.cleaned_data['content_text']
            else:
                message = "从HTML网页中读取数据是存在错误。"
                return render(request, 'on_this_today/add_new_event.html', {'message': message})
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
        return render(request, 'on_this_today/add_new_event.html', {'message': str(parsed_date) + " " + content_text})
    else:
        return render(request, 'on_this_today/add_new_event.html')


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
