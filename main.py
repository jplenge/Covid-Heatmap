import pandas as pd
import datetime

from bokeh.models import (BasicTicker,
                          ColorBar,
                          ColumnDataSource,
                          LinearColorMapper,
                          PrintfTickFormatter,
                          HoverTool,
                          Dropdown,
                          Select,
                          DateRangeSlider,
                          MultiSelect,
                          Div,
                          Button,
                          CustomJS)
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.palettes import inferno
from bokeh.io import curdoc
from bokeh.layouts import layout, column, row

import settings
from CovidCases import CovidCases

cases = CovidCases()


# Generate input controls
age_group_selector = Select(title="Altersgruppe", options=['Alle', 'A00-A04', 'A05-A14', 'A15-A34', 'A35-A59', 'A60-A79', 'A80+'], value='Alle')
gender_selector = Select(title="Geschlecht", options=['Alle', 'Männlich', 'Weiblich'], value='Alle')
mode_selector = Select(title="Kategorie", options=['Infektionsfälle', 'Todesfälle'], value='Infektionsfälle')

xaxis_selector = Select(title="x-Achse", options=['Bundesland', 'Kalenderwoche', 'Altersgruppe', 'Geschlecht'], value='Kalenderwoche')
yaxis_selector = Select(title="y-Achse", options=['Bundesland', 'Kalenderwoche', 'Altersgruppe', 'Geschlecht'], value='Bundesland')

state_selector = Select(title="Bundesland", options=['Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen'], value='Bremen')

date_range_slider = DateRangeSlider(value=((datetime.datetime.now() - datetime.timedelta(weeks=26)).date(), datetime.datetime.now().date()),
                                    start=datetime.date(2020, 1, 1),
                                    end= datetime.datetime.now().date())

state_multiselect =  MultiSelect(value=[], options=['Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen'])

week_selector = Select(title="Kalenderwoche", options=cases.week_list, value=cases.week_list[-1])

reset_states_button = Button(label="Bundesländer zurücksetzen", button_type="success")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], inzidenz=[], cases=[], population=[]))

hover = HoverTool(
    tooltips=[("Inzidenz", "@inzidenz{%0.2f}"),
              ("Bundesland", "@y"),
              ("Woche:", "@x"),
              ("Fälle:", "@cases"),
              ("Bevölkerunganzahl:", "@population")
             ],
    formatters={'@inzidenz': 'printf'}
)


mapper = LinearColorMapper(
    palette=inferno(256),
    low=0,
    high=500
)

p = figure(
	width=900,
	height=400,
	title="Covid-Fälle",
	x_range=[],
	y_range=[],
	toolbar_location=None,
	tools="",
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

p.tools.append(hover)

color_bar = ColorBar(color_mapper=mapper,
                     ticker=BasicTicker(),
                     title="Infektionen / 100000 Einwohner / Woche")

p.add_layout(color_bar, 'right')


gender_map = {
    'Alle' : 'Alle',
    'Männlich' : 'M',
    'Weiblich' : 'W'
}


def update():

    if mode_selector.value == 'Infektionsfälle':
        df = cases.select_infection_data({'Alle' : 'gesamt'}.get(age_group_selector.value, age_group_selector.value), gender_map.get(gender_selector.value))
        color_bar.title = "Infektionen / 100000 Einwohner / Woche"
    else:
        df = cases.select_death_data({'Alle' : 'gesamt'}.get(age_group_selector.value, age_group_selector.value), gender_map.get(gender_selector.value))
        color_bar.title = "Todesfälle / 100000 Einwohner / Woche"

    p.x_range.factors = cases.week_list 
    p.y_range.factors = list(reversed(df['Bundesland'].unique()))
    p.title.text = f"Kategorie: {mode_selector.value}, Altersgruppe: {age_group_selector.value}, Geschlecht: {gender_selector.value}"

    mapper.low=df['inzidenz'].max()
    mapper.high=df['inzidenz'].min()

    source.data = dict(
        x=df['week'],
        y=df['Bundesland'],
        inzidenz=df['inzidenz'],
        cases=df['cases'],
        population=df['population'],
        )
    update_week_range()


def update_both_axis():
    df = cases.select_infection_2axis_data(week_selector.value, gender_map.get(gender_selector.value))

    if (xaxis_selector.value == "Bundesland") & (yaxis_selector.value == "Altersgruppe"):
        mapper.low=df['inzidenz'].max()
        mapper.high=df['inzidenz'].min()

        source.data = dict(
            x=df['bundesland'],
            y=df['Altersgruppe'],
            inzidenz=df['inzidenz'],
            cases=df['cases'],
            population=df['population'],
        )



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

    p.x_range.factors = week_list

def update_state_range():
    p.y_range.factors = sorted(state_multiselect.value)

def reset_states():
    #p.y_range.factors = cases.states_list
    state_multiselect.value = []
    update()

xaxis_selector.on_change('value', lambda attr, old, new: update_both_axis())
yaxis_selector.on_change('value', lambda attr, old, new: update_both_axis())

mode_selector.on_change('value', lambda attr, old, new: update())
age_group_selector.on_change('value', lambda attr, old, new: update())
gender_selector.on_change('value', lambda attr, old, new: update())
date_range_slider.on_change('value', lambda attr, old, new: update_week_range())
state_multiselect.on_change('value', lambda attr, old, new: update_state_range())
reset_states_button.on_click(reset_states)

headline1 = Div(text="<H2>Einstellungen</H2>", width=220, height=50)
headline2 = Div(text="<H3>Weiteres</H3>", width=220, height=50)

intro = Div(text="<center> <H1>Covid Heatmap</H1> </center> <br> Diese Website übernimmt COVID-Informationen von der Website des Robert-Koch-Instituts (RKI) und schlüsselt sie sowohl für die Inzidenz- als auch für die Sterberate in die Kategorien Alter, Geschlecht, Bundesland und Zeit auf. Es ist schwierig, diese Faktoren gleichzeitig zu betrachten. Sie können also auswählen, welche Variablen für Sie am wichtigsten sind, um ein Diagramm der gesuchten Daten zu erstellen. Es gibt einige Wochen für bestimmte Gruppen, für die keine Daten erfasst wurden. Diese Punkte sind im Diagramm leer gelassen.<br> Auf der RKI-Website können wir die Zahl der geimpften und ungeimpften Fälle nicht abrufen. Wenn jemand weiß, wie man diese Informationen abrufen kann, lassen Sie es uns bitte wissen, damit wir sie auf der Website einfügen können. Sie können uns auch mitteilen, wenn Sie andere Vorschläge haben.", width=1200, height=180)

inputs = column([headline1,mode_selector, age_group_selector, gender_selector, state_multiselect, reset_states_button, headline2, state_selector, xaxis_selector, yaxis_selector, week_selector], width=220)

l = column([intro, row([inputs, column([p, date_range_slider])])])

update()

curdoc().add_root(l)
curdoc().title = "Covid"

