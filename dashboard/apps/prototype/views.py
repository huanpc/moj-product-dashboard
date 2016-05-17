import json
import datetime
from dateutil import relativedelta
import random
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect


def get_x_axis(date):

    x_axis = []

    x_axis.append(date.strftime('%B %Y'))

    for i in range(1, 11):
        date += relativedelta.relativedelta(months=1)
        x_axis.append(date.strftime('%B %Y'))

    return x_axis

class Index(TemplateView):

    template_name = 'index.html'


class DataResponse(View):

    def get(self, request, *args, **kwargs):

        date = datetime.datetime(2016, 1, 1, 12, 0, 0)

        # x_axis = ['January', 'February', 'March', 'April',
        #           'May', 'June', 'July', 'August', 'September',
        #           'October', 'November', 'December']

        x_axis = get_x_axis(date)

        y_axis = []

        for month in x_axis:

            y_axis.append(random.random() * 100)

        trace = {
            'x': x_axis,
            'y': y_axis,
            'type': 'bar',
        }

        layout = {
            # 'height': 350,
            # 'width': 350,
            'showlegend': False,

            'margin': {
                'l': 50,
                'r': 100,
                'b': 100,
                't': 100,
                'pad': 4
            },

            # 'paper_bgcolor': '#7f7f7f',
            # 'plot_bgcolor': '#c7c7c7',
        }

        response = {
            'data': [trace],
            'layout': layout,
        }

        return JsonResponse(response, safe=False)
