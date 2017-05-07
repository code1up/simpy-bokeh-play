"""DOCSTRING"""
from bokeh.layouts import column, gridplot
from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure
from bokeh.driving import count

BUFSIZE = 200

source = ColumnDataSource(dict(
    time=[],
    capacity=[]
))


def _create_prices(t):
    """DOCSTRING"""
    return t


@count()
def update(t):
    capacity = _create_prices(t)

    new_data = dict(
        time=[t],
        capacity=[t ** 2]
    )

    source.stream(new_data, 300)


def create_chart():
    p = figure(
        plot_height=500,
        tools="xpan,xwheel_zoom,xbox_zoom,reset",
        x_axis_type=None,
        y_axis_location="right")

    p.x_range.follow = "end"
    p.x_range.follow_interval = 100
    p.x_range.range_padding = 0

    p.line(
        x='time',
        y='capacity',
        alpha=0.2,
        line_width=3,
        color='navy',
        source=source)

    curdoc().add_root(column(gridplot(
        [[p]], toolbar_location="left", plot_width=1000)))

    curdoc().add_periodic_callback(update, 50)
    curdoc().title = "CAPACITY"

create_chart()
