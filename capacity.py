"""DOCSTRING"""
import bokeh.layouts
import bokeh.models
import bokeh.plotting
import bokeh.driving

BUFSIZE = 200

source = bokeh.models.ColumnDataSource(dict(
    time=[],
    capacity=[]
))


def get_capacity(time):
    """DOCSTRING"""
    return time


@bokeh.driving.count()
def update(time):
    """DOCSTRING"""
    capacity = get_capacity(time)

    new_data = dict(
        time=[time],
        capacity=[capacity]
    )

    source.stream(new_data, 300)


def create_chart():
    """DOCSTRING"""
    figure = bokeh.plotting.figure(
        plot_height=500,
        tools="xpan,xwheel_zoom,xbox_zoom,reset",
        x_axis_type=None,
        y_axis_location="right")

    figure.x_range.follow = "end"
    figure.x_range.follow_interval = 100
    figure.x_range.range_padding = 0

    figure.line(
        x='time',
        y='capacity',
        alpha=1.0,
        line_width=2,
        color='blue',
        source=source)

    document = bokeh.plotting.curdoc()

    gridplot = bokeh.layouts.gridplot(
        [[figure]],
        toolbar_location="left",
        plot_width=1000)

    column = bokeh.layouts.column(gridplot)

    document.add_root(column)
    document.add_periodic_callback(update, 50)
    document.title = "CAPACITY"


create_chart()
