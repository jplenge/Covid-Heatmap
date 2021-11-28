from tornado.ioloop import IOLoop

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.server.server import Server


def modify_doc(doc):
    """Add a plotted function to the document.

    Arguments:
        doc: A bokeh document to which elements can be added.
    """
    x_values = range(10)
    y_values = [x ** 2 for x in x_values]
    data_source = ColumnDataSource(data=dict(x=x_values, y=y_values))
    plot = figure(title="f(x) = x^2",
                  tools="crosshair,pan,reset,save,wheel_zoom",)
    plot.line('x', 'y', source=data_source, line_width=3, line_alpha=0.6)
    doc.add_root(plot)
    doc.title = "Test Plot"


def main():
    """Launch the server and connect to it.
    """
    print("Preparing a bokeh application.")
    io_loop = IOLoop.current()
    bokeh_app = Application(FunctionHandler(modify_doc))

    server = Server({"/": bokeh_app}, io_loop=io_loop)
    server.start()
    print("Opening Bokeh application on http://localhost:5006/")

    io_loop.add_callback(server.show, "/")
    io_loop.start()


main()