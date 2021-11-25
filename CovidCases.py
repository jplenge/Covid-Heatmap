import datetime
import pandas as pd

import settings

class CovidCases():
    """"docstring for CovidCases"""

    def __init__(self):
        self.df_rki_raw = pd.read_csv(settings.covid_data_path, parse_dates = ['Meldedatum', 'Datenstand', 'Refdatum'])
        self.df_rki_raw['week'] = self.df_rki_raw['Meldedatum'].apply(lambda x: str(x.isocalendar()[0]) + '-' + str(x.isocalendar()[1]).zfill(2))

        self.week_list = sorted(self.df_rki_raw['week'].unique().tolist())[:-1]
        self.states_list = sorted(self.df_rki_raw['Bundesland'].unique())

        # Read population data from csv file
        self.df_pop = pd.read_csv("/Users/jplenge/Documents/Programming/Python/Covid_Bokeh_App/data/Altersgruppen_insgesamt.csv")
        self.df_pop_m = pd.read_csv("/Users/jplenge/Documents/Programming/Python/Covid_Bokeh_App/data/Altersgruppen_maennlich.csv")
        self.df_pop_w = pd.read_csv("/Users/jplenge/Documents/Programming/Python/Covid_Bokeh_App/data/Altersgruppen_weiblich.csv")



    def get_agegroup_population(self, state_series, age_group, geschlecht):
        """Docstring"""

        population=[]

        for _, state in state_series.iteritems():
            if geschlecht == 'M':
                population.append(self.df_pop_m.query(f"Bundesland == '{state}'")[age_group].values[0])
            elif geschlecht == 'W':
                population.append(self.df_pop_w.query(f"Bundesland == '{state}'")[age_group].values[0])
            else:
                population.append(self.df_pop.query(f"Bundesland == '{state}'")[age_group].values[0])

        return population

    def select_infection_2axis_data(self, kalenderwoche, geschlecht):
        return self.df_rki_raw \
            .query(f"week == '{kalenderwoche}'") \
            .groupby(['Bundesland', 'Altersgruppe'], as_index=False) \
            .agg(cases=('AnzahlFall', 'sum')) \
            .query("Altersgruppe != 'unbekannt'") \
            .assign(population = lambda x: self.get_agegroup_population(x.Bundesland, x.Altersgruppe, f'{geschlecht}')) \
            .assign(inzidenz = lambda x: x.cases * 100000 / x.population)


    def select_infection_data(self, altersgruppe, geschlecht):
        """ select infection cases  """

        if altersgruppe == 'gesamt':
            print("Selected Altersgruppe", altersgruppe)
            selected =  self.df_rki_raw     # check if should use copy()
        else:
            selected = self.df_rki_raw.query(f"Altersgruppe == '{altersgruppe}'")

        if geschlecht == 'Alle':
            return selected \
                .groupby(['Bundesland', 'week'], as_index=False) \
                .agg(cases=('AnzahlFall', 'sum')) \
                .assign(population = lambda x: self.get_agegroup_population(x.Bundesland, f'{altersgruppe}', f'{geschlecht}')) \
                .assign(inzidenz = lambda x: x.cases * 100000 / x.population)
        else:
            return selected \
                .query(f"Geschlecht == '{geschlecht}'") \
                .groupby(['Bundesland', 'week'], as_index=False) \
                .agg(cases=('AnzahlFall', 'sum')) \
                .assign(population = lambda x: self.get_agegroup_population(x.Bundesland, f'{altersgruppe}', f'{geschlecht}')) \
                .assign(inzidenz = lambda x: x.cases * 100000 / x.population)


    def select_death_data(self, altersgruppe, geschlecht):
        """ select death cases  """

        if altersgruppe == 'gesamt':
            print("Selected Altersgruppe", altersgruppe)
            selected =  self.df_rki_raw     # check if should use copy()
        else:
            selected = self.df_rki_raw.query(f"Altersgruppe == '{altersgruppe}'")

        if geschlecht == 'Alle':
            return selected \
                .groupby(['Bundesland', 'week'], as_index=False) \
                .agg(cases=('AnzahlTodesfall', 'sum')) \
                .assign(population = lambda x: self.get_agegroup_population(x.Bundesland, f'{altersgruppe}', f'{geschlecht}')) \
                .assign(inzidenz = lambda x: x.cases * 100000 / x.population)
        else:
            return selected \
                .query(f"Geschlecht == '{geschlecht}'") \
                .groupby(['Bundesland', 'week'], as_index=False) \
                .agg(cases=('AnzahlTodesfall', 'sum')) \
                .assign(population = lambda x: self.get_agegroup_population(x.Bundesland, f'{altersgruppe}', f'{geschlecht}')) \
                .assign(inzidenz = lambda x: x.cases * 100000 / x.population)


