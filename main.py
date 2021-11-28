import pandas as pd
import datetime

from bokeh.models import (BasicTicker,
                          ColorBar,
                          ColumnDataSource,
                          LinearColorMapper,
                          LogColorMapper,
                          PrintfTickFormatter,
                          HoverTool,
                          Dropdown,
                          Select,
                          DateRangeSlider,
                          MultiSelect,
                          Div,
                          Button,
                          Spacer,
                          CustomJS)
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.palettes import inferno, mpl
from bokeh.io import curdoc
from bokeh.layouts import layout, column, row

from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from tornado.ioloop import IOLoop

import settings
from CovidCases import CovidCases

cases = CovidCases()


def main_app(doc):

    # change status of widgets

    def change_widget_status(age_group_selector_disabled, gender_selector_disabled, state_multiselect_disabled,reset_states_button_disabled, 
        state_selector_disabled, week_selector_disabled, date_range_slider_disabled):

        age_group_selector.disabled = age_group_selector_disabled
        gender_selector.disabled = gender_selector_disabled
        state_multiselect.disabled = state_multiselect_disabled
        reset_states_button.disabled =  reset_states_button_disabled
        state_selector.disabled = state_selector_disabled  
        week_selector.disabled = week_selector_disabled  
        date_range_slider.disabled = date_range_slider_disabled


    def update_widgets():
        if xaxis_selector.value == yaxis_selector.value:
            generate_heatmap_button.disabled = True
            return
        else:
            generate_heatmap_button.disabled = False


        if (xaxis_selector.value in ['Bundesland', 'Meldewoche']) and yaxis_selector.value in ['Bundesland', 'Meldewoche']:
            change_widget_status(False, False, False, False, True, True, False)
            return

        if (xaxis_selector.value in ['Bundesland', 'Altersgruppe']) and yaxis_selector.value in ['Bundesland', 'Altersgruppe']:
            change_widget_status(True, False, False, False, True, False, True)
            return 

        if (xaxis_selector.value in ['Bundesland', 'Geschlecht']) and yaxis_selector.value in ['Bundesland', 'Geschlecht']:
            change_widget_status(False, True, False, False, True, False, True)
            return 

        if (xaxis_selector.value in ['Meldewoche', 'Altersgruppe']) and yaxis_selector.value in ['Meldewoche', 'Altersgruppe']:
            change_widget_status(True, False, True, True, False, True, False)
            return 

        if (xaxis_selector.value in ['Meldewoche', 'Geschlecht']) and yaxis_selector.value in ['Meldewoche', 'Geschlecht']:
            change_widget_status(False, True, True, True, False, True, False)
            return 

        if (xaxis_selector.value in ['Altersgruppe', 'Geschlecht']) and yaxis_selector.value in ['Altersgruppe', 'Geschlecht']:
            change_widget_status(True, True, True, True, False, False, True)
            return 


    def update_hovertool(cat_name1, cat1, cat_name2, cat2):
          hover.tooltips = [("Inzidenz", "@inzidenz{%0.2f}"),
                  (f"{cat_name1}:", f"@{cat1}"),
                  (f"{cat_name2}:", f"@{cat2}"),
                  ("Fälle:", "@cases"),
                  ("Einwohnerzahl:", "@population")
                ]


    # functions to update data
    def update():

        if mode_selector.value == 'Infektionsfälle':
            #color_bar.title = "Infektionen / 100000 Einwohner / Woche"
            color_bar.title  = "Fälle / 100000 Einwohner / Woche"
        else:
            color_bar.title  = "Fälle / 100000 Einwohner / Woche"

        selected_week = {'Alle': f"{cases.week_list[1]}-{cases.week_list[-1]}"}.get(week_selector.value, week_selector.value)


        if (xaxis_selector.value in ['Bundesland', 'Meldewoche']) and yaxis_selector.value in ['Bundesland', 'Meldewoche']:

            df = cases.select_state_week_data({'Alle' : 'gesamt'}.get(age_group_selector.value, age_group_selector.value), gender_map.get(gender_selector.value), mode_selector.value )

            if xaxis_selector.value == "Bundesland":
                x_axis = df['Bundesland']
                y_axis = df['week']
     
                p.x_range.factors = list(reversed(df['Bundesland'].unique()))
                p.y_range.factors = cases.week_list 

                update_hovertool('Bundesland', 'x', 'Meldewoche', 'y')
            else:
                x_axis = df['week']
                y_axis = df['Bundesland']
                p.x_range.factors = cases.week_list 
                p.y_range.factors = list(reversed(df['Bundesland'].unique()))

                update_hovertool('Bundesland', 'y', 'Meldewoche', 'x') 

            p.title.text = f"Kategorie: {mode_selector.value}, Altersgruppe: {age_group_selector.value}, Geschlecht: {gender_selector.value}"           


        if (xaxis_selector.value in ['Bundesland', 'Altersgruppe']) and yaxis_selector.value in ['Bundesland', 'Altersgruppe']:
            df = cases.select_state_agegroup_data(gender_map.get(gender_selector.value),  week_selector.value, mode_selector.value )

            if xaxis_selector.value == "Bundesland":
                x_axis = df['Bundesland']
                y_axis = df['Altersgruppe']
     
                p.x_range.factors = list(reversed(df['Bundesland'].unique()))
                p.y_range.factors = settings.agegroup_list

                update_hovertool('Bundesland', 'x', 'Altersgruppe', 'y')
            else:
                x_axis = df['Altersgruppe']
                y_axis = df['Bundesland']
                p.x_range.factors = settings.agegroup_list
                p.y_range.factors = list(reversed(df['Bundesland'].unique()))

                update_hovertool('Bundesland', 'y', 'Altersgruppe', 'x')


            
            p.title.text = f"Kategorie: {mode_selector.value}, Meldewoche: {week_selector.value}, Geschlecht: {gender_selector.value}, Meldewoche: {selected_week}"



        if (xaxis_selector.value in ['Bundesland', 'Geschlecht']) and yaxis_selector.value in ['Bundesland', 'Geschlecht']:

            df = cases.select_state_gender_data({'Alle' : 'gesamt'}.get(age_group_selector.value, age_group_selector.value),  week_selector.value, mode_selector.value )

            if xaxis_selector.value == "Bundesland":
                x_axis = df['Bundesland']
                y_axis = df['Geschlecht']
     
                p.x_range.factors = list(reversed(df['Bundesland'].unique()))
                p.y_range.factors = ['M', 'W']

                update_hovertool('Bundesland', 'x', 'Geschlecht', 'y')

            else:
                x_axis = df['Geschlecht']
                y_axis = df['Bundesland']
                p.x_range.factors = ['M', 'W']
                p.y_range.factors = list(reversed(df['Bundesland'].unique()))

                update_hovertool('Bundesland', 'y', 'Geschlecht', 'x')

            p.title.text = f"Kategorie: {mode_selector.value}, Altersgruppe: {age_group_selector.value}, Meldewoche: {selected_week}"


        if (xaxis_selector.value in ['Meldewoche', 'Altersgruppe']) and yaxis_selector.value in ['Meldewoche', 'Altersgruppe']:

            df = cases.select_week_agegroup_data(gender_map.get(gender_selector.value),state_selector.value, mode_selector.value )

            if xaxis_selector.value == "Meldewoche":
                x_axis = df['week']
                y_axis = df['Altersgruppe']
     
                p.x_range.factors = cases.week_list 
                p.y_range.factors = settings.agegroup_list

                update_hovertool('Meldewoche', 'x', 'Altersgruppe', 'y')

            else:
                x_axis = df['Altersgruppe']
                y_axis = df['week']
                p.x_range.factors = settings.agegroup_list
                p.y_range.factors = cases.week_list

                update_hovertool('Meldewoche', 'y', 'Altersgruppe', 'x')

            p.title.text = f"Kategorie: {mode_selector.value}, Bundesland: {state_selector.value},  Geschlecht: {gender_selector.value}"



        if (xaxis_selector.value in ['Meldewoche', 'Geschlecht']) and yaxis_selector.value in ['Meldewoche', 'Geschlecht']:

            df = cases.select_week_gender_data({'Alle' : 'gesamt'}.get(age_group_selector.value, age_group_selector.value), state_selector.value, mode_selector.value )

            if xaxis_selector.value == "Meldewoche":
                x_axis = df['week']
                y_axis = df['Geschlecht']
     
                p.x_range.factors = cases.week_list 
                p.y_range.factors = ['M', 'W']

                update_hovertool('Meldewoche', 'x', 'Geschlecht', 'y')

            else:
                x_axis = df['Geschlecht']
                y_axis = df['week']
                p.x_range.factors = ['M', 'W']
                p.y_range.factors = cases.week_list  

                update_hovertool('Meldewoche', 'y', 'Geschlecht', 'x')

                p.title.text = f"Kategorie: {mode_selector.value}, Bundesland: {state_selector.value}, Altersgruppe: {age_group_selector.value}"



        if (xaxis_selector.value in ['Altersgruppe', 'Geschlecht']) and yaxis_selector.value in ['Altersgruppe', 'Geschlecht']:

            df = cases.select_agegroup_gender_data(week_selector.value, state_selector.value, mode_selector.value )

            if xaxis_selector.value == "Altersgruppe":
                x_axis = df['Altersgruppe']
                y_axis = df['Geschlecht']
     
                p.x_range.factors = settings.agegroup_list
                p.y_range.factors = ['M', 'W']

                update_hovertool('Altersgruppe', 'x', 'Geschlecht', 'y')

            else:
                x_axis = df['Geschlecht']
                y_axis = df['Altersgruppe']

                p.x_range.factors = ['M', 'W']
                p.y_range.factors = settings.agegroup_list  

                update_hovertool('Altersgruppe', 'y', 'Geschlecht', 'x')


            p.title.text = f"Kategorie: {mode_selector.value},  Bundesland: {state_selector.value}, Meldewoche: {selected_week}"


        mapper.low=df['inzidenz'].min()
        mapper.high=df['inzidenz'].max()

        source.data = dict(
            x=x_axis,
            y=y_axis,
            inzidenz=df['inzidenz'],
            cases=df['cases'],
            population=df['population'],
            )

        update_week_range()


    def update_week_range():
        start_year = datetime.datetime.fromtimestamp(date_range_slider.value[0]/1e3).isocalendar().year
        start_week = datetime.datetime.fromtimestamp(date_range_slider.value[0]/1e3).isocalendar().week
        end_year = datetime.datetime.fromtimestamp(date_range_slider.value[1]/1e3).isocalendar().year
        end_week = datetime.datetime.fromtimestamp(date_range_slider.value[1]/1e3).isocalendar().week

        week_list = []

        if start_year == end_year:
            week_list = [f"{start_year}-{week:02d}" for week in range(start_week,end_week+1)]
        else:
            stop_week = datetime.date(start_year,12,31).isocalendar().week
            week_list = [f"{start_year}-{week:02d}" for week in range(start_week,stop_week+1)]
            week_list += [f"{end_year}-{week:02d}" for week in range(1,end_week+1)]

        
        if xaxis_selector.value == "Meldewoche":
            p.x_range.factors = week_list
        elif yaxis_selector.value == "Meldewoche":
            p.y_range.factors = week_list


    def update_state_range():
        if xaxis_selector.value == "Bundesland":
            p.x_range.factors = sorted(state_multiselect.value)
        elif yaxis_selector.value == "Bundesland":
            p.y_range.factors = sorted(state_multiselect.value)
        
        
    def reset_states():
        state_multiselect.value = []
        update()


    # Generate input controls
    age_group_selector = Select(
        title="Altersgruppe",
        options=['Alle', 'A00-A04', 'A05-A14', 'A15-A34', 'A35-A59', 'A60-A79', 'A80+'], 
        value='Alle')

    gender_selector = Select(
        title="Geschlecht", 
        options=['Alle', 'Männlich', 'Weiblich'], 
        value='Alle')

    mode_selector = Select(
        title="Kategorie", 
        options=['Infektionsfälle', 'Todesfälle'], value='Infektionsfälle')

    xaxis_selector = Select(
        title="x-Achse", 
        options=['Bundesland', 'Meldewoche', 'Altersgruppe', 'Geschlecht'], 
        value='Meldewoche')

    yaxis_selector = Select(
        title="y-Achse", 
        options=['Bundesland', 'Meldewoche', 'Altersgruppe', 'Geschlecht'], 
        value='Bundesland')

    state_selector = Select(
        title="Bundesland", 
        options=['Alle'] + settings.state_list, 
        value='Bremen')

    date_range_slider = DateRangeSlider(
        value=((datetime.datetime.now() - datetime.timedelta(weeks=12)).date(), (datetime.datetime.now() - datetime.timedelta(weeks=1)).date()) ,
        start=datetime.date(2020, 1, 1),
        end= (datetime.datetime.now() - datetime.timedelta(weeks=1)).date(),
        format = '%Y-%W',
        step=7)

    state_multiselect =  MultiSelect(
        title="Bundesländer Auswahl",
        value=[], 
        options=settings.state_list, 
        height=160)

    week_selector = Select(
        title="Kalenderwoche", 
        options=cases.week_list + ['Alle'], 
        value=cases.week_list[-1])

    reset_states_button = Button(
        label="Bundesländer zurücksetzen", 
        button_type="success")

    generate_heatmap_button = Button(
        label="Heatmap erzeugen", 
        button_type="success", 
        width=160, 
        height=50)



    # Create Column Data Source that will be used by the plot
    source = ColumnDataSource(data=dict(x=[], y=[], inzidenz=[], cases=[], population=[]))

    # Setup 
    hover = HoverTool(
        tooltips=[("Inzidenz", "@inzidenz{%0,0.2f}"),
                  ("Bundesland", "@y"),
                  ("Woche:", "@x"),
                  ("Fälle:", "@cases{%0,0.0f}"),
                  ("Einwohnerzahl:", "@population")
                 ],
        formatters={'@inzidenz': 'printf'}
    )


    mapper = LinearColorMapper(
        palette='Turbo256',  #inferno(256),
        low=0,
        high=500,
        nan_color = 'gray'
    )

    p = figure(
        width=750,
        height=400,
        title="Covid-Fälle",
        x_range=[],
        y_range=[],
        toolbar_location='right',
        tools="save",
        x_axis_location='below'
        )

    p.rect(
        x='x',
        y='y',
        width=1,
        height=1,
        source=source,
        line_color=None,
        fill_color=transform('inzidenz', mapper)
        )

    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "12px"
    p.xaxis.major_label_orientation = 1.0

    p.title.text_font_size = "14px"

    p.tools.append(hover)

    color_bar = ColorBar(color_mapper=mapper,
                         ticker=BasicTicker()
                         )

    p.add_layout(color_bar, 'right')


    # 
    gender_map = {
        'Alle' : 'Alle',
        'Männlich' : 'M',
        'Weiblich' : 'W'
    }



    xaxis_selector.on_change('value', lambda attr, old, new: update_widgets())
    yaxis_selector.on_change('value', lambda attr, old, new: update_widgets())


    date_range_slider.on_change('value', lambda attr, old, new: update_week_range())
    state_multiselect.on_change('value', lambda attr, old, new: update_state_range())
    reset_states_button.on_click(reset_states)
    generate_heatmap_button.on_click(update)



    headline2 = Div(text="<H2>Filtermöglichkeiten</H2> ", width=100, height=50)

    main_inputs = row([mode_selector, xaxis_selector, yaxis_selector, generate_heatmap_button], width=800)

    filter_left = column([headline2, age_group_selector, gender_selector])
    filter_middle = column([state_multiselect, reset_states_button])
    filter_right = column([state_selector, week_selector, date_range_slider])

    filter_inputs = row([filter_left, filter_middle, filter_right], width=800)

    l = column([Spacer(height=20), main_inputs, Spacer(height=20), row([p], width=800, sizing_mode="scale_width"), Spacer(height=20), filter_inputs], width=800) 

    update_widgets()
    update()

    doc.add_root(l)
    doc.title = "Covid Heatmap"
    doc.templates = "./templates/index.html"


print("Preparing a bokeh application.")
io_loop = IOLoop.current()
bokeh_app = Application(FunctionHandler(main_app))

server = Server({"/": bokeh_app}, io_loop=io_loop, port=9001)
server.start()

io_loop.add_callback(server.show, "/")
io_loop.start()

