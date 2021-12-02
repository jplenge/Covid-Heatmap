#!/Users/jplenge/.pyenv/shims/python
import pandas as pd
import datetime

use_col = ['Bundesland','Altersgruppe', 'Geschlecht', 'AnzahlFall', 'AnzahlTodesfall', 'Meldedatum'] 
current_week =  f"{datetime.datetime.now().isocalendar()[0]}-{str(datetime.datetime.now().isocalendar()[1]).zfill(2)}"


df = pd.read_csv("https://www.arcgis.com/sharing/rest/content/items/f10774f1c63e40168479a1feb6c7ca74/data", usecols = use_col, parse_dates = ['Meldedatum'])
df['week'] = df['Meldedatum'].apply(lambda x: str(x.isocalendar()[0]) + '-' + str(x.isocalendar()[1]).zfill(2))
df=df.query(f"week != '{current_week}'")


df.groupby(['Bundesland','Altersgruppe', 'Geschlecht','week'], as_index=False)[['AnzahlFall', 'AnzahlTodesfall']].sum() \
    .to_csv("data/RKI_COVID19.csv")
