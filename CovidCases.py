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



    # 
    #   Calculate population date for age groups
    #
    def get_agegroup_population(self, state_series, age_group, geschlecht):
        """Docstring"""

        population=[]

        if isinstance(state_series, pd.Series):

            if isinstance(age_group, pd.Series):
                # in this case geslchecht is ont a pd.series
                for state, age_group_item in zip(state_series.tolist(), age_group.tolist()):
                    if geschlecht == 'M':
                        population.append(self.df_pop_m.query(f"Bundesland == '{state}'")[age_group_item].values[0])
                    elif geschlecht == 'W':
                        population.append(self.df_pop_w.query(f"Bundesland == '{state}'")[age_group_item].values[0])
                    else:
                        population.append(self.df_pop.query(f"Bundesland == '{state}'")[age_group_item].values[0])
            else:
                if isinstance(geschlecht, pd.Series):
                    for state, gender in zip(state_series.tolist(), geschlecht.tolist()):
                        if gender == 'M':
                            population.append(self.df_pop_m.query(f"Bundesland == '{state}'")[age_group].values[0])
                        elif gender == 'W':
                            population.append(self.df_pop_w.query(f"Bundesland == '{state}'")[age_group].values[0])
                        else:
                            population.append(self.df_pop.query(f"Bundesland == '{state}'")[age_group].values[0])
                else:      
                    for _, state in state_series.iteritems():
                        if geschlecht == 'M':
                            population.append(self.df_pop_m.query(f"Bundesland == '{state}'")[age_group].values[0])
                        elif geschlecht == 'W':
                            population.append(self.df_pop_w.query(f"Bundesland == '{state}'")[age_group].values[0])
                        else:
                            population.append(self.df_pop.query(f"Bundesland == '{state}'")[age_group].values[0])
        else:
            # f'{bundesland}', f'{altersgruppe}', x.Geschlecht
            if isinstance(age_group, pd.Series):
                if isinstance(geschlecht, pd.Series):
                    for age_group_item, gender in zip(age_group.tolist(), geschlecht.tolist()):
                        if gender == 'M':
                            population.append(self.df_pop_m.query(f"Bundesland == '{state_series}'")[age_group_item].values[0])
                        elif gender == 'W':
                            population.append(self.df_pop_w.query(f"Bundesland == '{state_series}'")[age_group_item].values[0])
                        else:
                            population.append(self.df_pop.query(f"Bundesland == '{state_series}'")[age_group_item].values[0])
                else:
                    for _, age_group_item in age_group.iteritems():
                        if geschlecht == 'M':
                            population.append(self.df_pop_m.query(f"Bundesland == '{state_series}'")[age_group_item].values[0])
                        elif geschlecht == 'W':
                            population.append(self.df_pop_w.query(f"Bundesland == '{state_series}'")[age_group_item].values[0])
                        else:
                            population.append(self.df_pop.query(f"Bundesland == '{state_series}'")[age_group_item].values[0])
            else:
                for _, gender_item in geschlecht.iteritems():
                    if gender_item == 'M':
                        population.append(self.df_pop_m.query(f"Bundesland == '{state_series}'")[age_group].values[0])
                    elif gender_item == 'W':
                        population.append(self.df_pop_w.query(f"Bundesland == '{state_series}'")[age_group].values[0])
                    else:
                        population.append(self.df_pop.query(f"Bundesland == '{state_series}'")[age_group].values[0])


        return population



    def select_state_week_data(self, altersgruppe, geschlecht, kategorie):
        """ select infection cases  """

        if altersgruppe == 'gesamt':
            selected =  self.df_rki_raw     # check if should use copy()
        else:
            selected = self.df_rki_raw.query(f"Altersgruppe == '{altersgruppe}'")

        if geschlecht == 'Alle':
            selected = selected \
                .groupby(['Bundesland', 'week'], as_index=False)
        else:
            selected = selected \
                .query(f"Geschlecht == '{geschlecht}'") \
                .groupby(['Bundesland', 'week'], as_index=False) 

        if kategorie == 'Infektionsfälle':
            selected = selected.agg(cases=('AnzahlFall', 'sum'))
        else:
            selected = selected.agg(cases=('AnzahlTodesfall', 'sum'))

        return selected \
            .assign(population = lambda x: self.get_agegroup_population(x.Bundesland, f'{altersgruppe}', f'{geschlecht}')) \
            .assign(inzidenz = lambda x: x.cases * 100000 / x.population)


    def select_state_agegroup_data(self, geschlecht, meldewoche, kategorie):
        """ select infection cases  """

        selected = self.df_rki_raw \
            .query(f"week == '{meldewoche}'") \
            .query("Altersgruppe != 'unbekannt'") \

        if geschlecht == 'Alle':
            selected = selected \
                .groupby(['Bundesland', 'Altersgruppe'], as_index=False)
        else:
            selected = selected \
                .query(f"Geschlecht == '{geschlecht}'") \
                .groupby(['Bundesland', 'Altersgruppe'], as_index=False) 

        if kategorie == 'Infektionsfälle':
            selected = selected.agg(cases=('AnzahlFall', 'sum'))
        else:
            selected = selected.agg(cases=('AnzahlTodesfall', 'sum'))

        return selected \
            .assign(population = lambda x: self.get_agegroup_population(x.Bundesland, x.Altersgruppe, f'{geschlecht}')) \
            .assign(inzidenz = lambda x: x.cases * 100000 / x.population)


    def select_state_gender_data(self, altersgruppe, meldewoche, kategorie):
        """ select infection cases  """

        # check if should use copy()
        if altersgruppe == 'gesamt':
            selected =  self.df_rki_raw \
                .query(f"week == '{meldewoche}'") \
                .groupby(['Bundesland', 'Geschlecht'], as_index=False)
        else:
            selected = self.df_rki_raw \
                .query(f"week == '{meldewoche}'") \
                .query(f"Altersgruppe == '{altersgruppe}'") \
                .groupby(['Bundesland', 'Geschlecht'], as_index=False)   

        if kategorie == 'Infektionsfälle':
            selected = selected.agg(cases=('AnzahlFall', 'sum'))
        else:
            selected = selected.agg(cases=('AnzahlTodesfall', 'sum'))

        return selected \
            .assign(population = lambda x: self.get_agegroup_population(x.Bundesland, f'{altersgruppe}', x.Geschlecht)) \
            .assign(inzidenz = lambda x: x.cases * 100000 / x.population)


    def select_week_agegroup_data(self, geschlecht, bundesland, kategorie):
        """ select infection cases  """

        selected = self.df_rki_raw \
            .query(f"Bundesland == '{bundesland}'") \
            .query("Altersgruppe != 'unbekannt'") 

        if geschlecht == 'Alle':
            selected = selected \
                .groupby(['week', 'Altersgruppe'], as_index=False)
        else:
            selected = selected \
                .query(f"Geschlecht == '{geschlecht}'") \
                .groupby(['week', 'Altersgruppe'], as_index=False) 
 
        if kategorie == 'Infektionsfälle':
            selected = selected.agg(cases=('AnzahlFall', 'sum'))
        else:
            selected = selected.agg(cases=('AnzahlTodesfall', 'sum'))

        return selected \
            .assign(population = lambda x: self.get_agegroup_population(f'{bundesland}', x.Altersgruppe, f'{geschlecht}')) \
            .assign(inzidenz = lambda x: x.cases * 100000 / x.population)



    def select_week_gender_data(self, altersgruppe, bundesland, kategorie):
        """ select infection cases  """

        if altersgruppe == 'gesamt':
            selected =  self.df_rki_raw \
                .query(f"Bundesland == '{bundesland}'") \
                .groupby(['week', 'Geschlecht'], as_index=False) 
        else:
            selected = self.df_rki_raw \
                .query(f"Altersgruppe == '{altersgruppe}'") \
                .query(f"Bundesland == '{bundesland}'") \
                .groupby(['week', 'Geschlecht'], as_index=False) 

        if kategorie == 'Infektionsfälle':
            selected = selected.agg(cases=('AnzahlFall', 'sum'))
        else:
            selected = selected.agg(cases=('AnzahlTodesfall', 'sum'))

        return selected \
            .assign(population = lambda x: self.get_agegroup_population(f'{bundesland}', f'{altersgruppe}', x.Geschlecht)) \
            .assign(inzidenz = lambda x: x.cases * 100000 / x.population)


    def select_agegroup_gender_data(self, meldewoche, bundesland, kategorie):
        """ select infection cases  """

        selected = self.df_rki_raw \
            .query(f"week == '{meldewoche}'") \
            .query(f"Bundesland == '{bundesland}'") \
            .query("Altersgruppe != 'unbekannt'") \
            .groupby(['Altersgruppe', 'Geschlecht'], as_index=False) 

        if kategorie == 'Infektionsfälle':
            selected = selected.agg(cases=('AnzahlFall', 'sum'))
        else:
            selected = selected.agg(cases=('AnzahlTodesfall', 'sum'))

        return selected \
            .assign(population = lambda x: self.get_agegroup_population(f'{bundesland}', x.Altersgruppe, x.Geschlecht)) \
            .assign(inzidenz = lambda x: x.cases * 100000 / x.population)
