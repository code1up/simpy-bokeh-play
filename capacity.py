"""DOCSTRING"""
from random import random

import bokeh.layouts
import bokeh.models
import bokeh.plotting
import bokeh.driving

import simpy

from sim import MessageQueue, Message

QUEUE_CAPACITY_BYTES = 4096
MESSAGE_BLOCK_SIZE = 1024
MESSAGE_BLOCK_TIMEOUT = 200

BUFSIZE = 200

source = bokeh.models.ColumnDataSource(dict(
    time=[],
    capacity=[],
    count=[]
))

env = simpy.Environment()
queue = MessageQueue(env=env, capacityBytes=QUEUE_CAPACITY_BYTES)


def get_capacity(time):
    """DOCSTRING"""
    return time


@bokeh.driving.count()
def update_chart(time):
    """DOCSTRING"""
    env.run(until=time)

    capacity = 4096 - queue.capacity.level  # get_capacity(time)
    count = len(queue.capacity.get_queue)

    new_data = dict(
        time=[time],
        capacity=[capacity],
        count=[count]
    )

    source.stream(new_data, 300)

    if random() > 0.9:
        size = int((MESSAGE_BLOCK_SIZE * 4) * random())
        message = Message(correlation_id=time, size=size)

        env.process(queue.queue_message(message=message))


def create_chart():
    """DOCSTRING"""
    figure = bokeh.plotting.figure(
        plot_height=500,
        tools="xpan,xwheel_zoom,xbox_zoom,reset",
        x_axis_type=None,
        y_axis_location="right",
        y_range=(0, 5000))

    figure.x_range.follow = "end"
    figure.x_range.follow_interval = 30000
    figure.x_range.range_padding = 0

    figure.extra_y_ranges = {
        'count': bokeh.models.Range1d(start=0, end=100)
    }

    figure.line(
        x='time',
        y='capacity',
        alpha=1.0,
        line_width=2,
        color='blue',
        source=source)

    figure.line(
        x='time',
        y='count',
        alpha=1.0,
        line_width=2,
        color='red',
        y_range_name='count',
        source=source)

    figure.add_layout(
        bokeh.models.LinearAxis(y_range_name='count'), 'left')

    document = bokeh.plotting.curdoc()

    figure.xaxis.axis_label = 't'

    gridplot = bokeh.layouts.gridplot(
        [[figure]],
        toolbar_location="left",
        plot_width=1000)

    column = bokeh.layouts.column(gridplot)

    document.add_root(column)
    document.add_periodic_callback(update_chart, 10)
    document.title = "CAPACITY"


create_chart()

message_a = Message(correlation_id='A', size=MESSAGE_BLOCK_SIZE - 1)
message_b = Message(correlation_id='B', size=(MESSAGE_BLOCK_SIZE * 4) + 1)
message_c = Message(correlation_id='C', size=MESSAGE_BLOCK_SIZE)
message_d = Message(correlation_id='D', size=MESSAGE_BLOCK_SIZE + 1)
message_e = Message(correlation_id='E', size=MESSAGE_BLOCK_SIZE - 1)


env.process(queue.queue_message(message=message_a))
env.process(queue.queue_message(message=message_b))
env.process(queue.queue_message(message=message_c))
env.process(queue.queue_message(message=message_d))
env.process(queue.queue_message(message=message_e))
