import datetime
import pandas as pd
from pathlib import PurePath

import settings


class CovidCases:
    """ "docstring for CovidCases"""

    def __init__(self):
        self.df_rki_raw = pd.read_csv(
            PurePath(settings.covid_data_path, "RKI_COVID19.csv")
        )
        # self.df_rki_raw['week'] = self.df_rki_raw['Meldedatum'].apply(lambda x: str(x.isocalendar()[0]) + '-' + str(x.isocalendar()[1]).zfill(2))

        self.hospitalisierung = pd.read_csv(
            PurePath(settings.covid_data_path, "Hospitalisierung.csv")
        )

        self.week_list = sorted(self.df_rki_raw["week"].unique().tolist())

        self.states_list = sorted(self.df_rki_raw["Bundesland"].unique())

        # Read population data from csv file
        self.df_pop = pd.read_csv(
            PurePath(settings.covid_data_path, "Altersgruppen_insgesamt.csv")
        )
        self.df_pop_m = pd.read_csv(
            PurePath(settings.covid_data_path, "Altersgruppen_maennlich.csv")
        )
        self.df_pop_w = pd.read_csv(
            PurePath(settings.covid_data_path, "Altersgruppen_weiblich.csv")
        )

    def get_agegroup_population(self, state_series, age_group, geschlecht):
        """
        get population size for specified age group
        returns pandas series  with populatino size
        age_group = ['A00-A04', 'A05-A14', 'A15-A34', 'A35-A59', 'A60-A79', 'A80+']
        state_series = ['Alle', 'Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen']
        geschlecht = ['M', 'W']

        """

        population = []

        if isinstance(state_series, pd.Series):
            if isinstance(age_group, pd.Series):
                for state, age_group_item in zip(
                    state_series.tolist(), age_group.tolist()
                ):
                    if geschlecht == "M":
                        population.append(
                            self.df_pop_m.query(f"Bundesland == '{state}'")[
                                age_group_item
                            ].values[0]
                        )
                    elif geschlecht == "W":
                        population.append(
                            self.df_pop_w.query(f"Bundesland == '{state}'")[
                                age_group_item
                            ].values[0]
                        )
                    else:
                        population.append(
                            self.df_pop.query(f"Bundesland == '{state}'")[
                                age_group_item
                            ].values[0]
                        )
            else:
                if isinstance(geschlecht, pd.Series):
                    for state, gender in zip(
                        state_series.tolist(), geschlecht.tolist()
                    ):
                        if gender == "M":
                            population.append(
                                self.df_pop_m.query(f"Bundesland == '{state}'")[
                                    age_group
                                ].values[0]
                            )
                        elif gender == "W":
                            population.append(
                                self.df_pop_w.query(f"Bundesland == '{state}'")[
                                    age_group
                                ].values[0]
                            )
                        else:
                            population.append(
                                self.df_pop.query(f"Bundesland == '{state}'")[
                                    age_group
                                ].values[0]
                            )
                else:
                    for _, state in state_series.iteritems():
                        if geschlecht == "M":
                            population.append(
                                self.df_pop_m.query(f"Bundesland == '{state}'")[
                                    age_group
                                ].values[0]
                            )
                        elif geschlecht == "W":
                            population.append(
                                self.df_pop_w.query(f"Bundesland == '{state}'")[
                                    age_group
                                ].values[0]
                            )
                        else:
                            population.append(
                                self.df_pop.query(f"Bundesland == '{state}'")[
                                    age_group
                                ].values[0]
                            )
        else:
            if isinstance(age_group, pd.Series):
                if isinstance(geschlecht, pd.Series):
                    for age_group_item, gender in zip(
                        age_group.tolist(), geschlecht.tolist()
                    ):
                        if state_series == "Alle":
                            if gender == "M":
                                population.append(self.df_pop_m[age_group_item].sum())
                            elif gender == "W":
                                population.append(self.df_pop_w[age_group_item].sum())
                            else:
                                population.append(self.df_pop[age_group_item].sum())
                        else:
                            if gender == "M":
                                population.append(
                                    self.df_pop_m.query(
                                        f"Bundesland == '{state_series}'"
                                    )[age_group_item].values[0]
                                )
                            elif gender == "W":
                                population.append(
                                    self.df_pop_w.query(
                                        f"Bundesland == '{state_series}'"
                                    )[age_group_item].values[0]
                                )
                            else:
                                population.append(
                                    self.df_pop.query(
                                        f"Bundesland == '{state_series}'"
                                    )[age_group_item].values[0]
                                )
                else:
                    for _, age_group_item in age_group.iteritems():
                        if state_series == "Alle":
                            if geschlecht == "M":
                                population.append(self.df_pop_m[age_group_item].sum())
                            elif geschlecht == "W":
                                population.append(self.df_pop_w[age_group_item].sum())
                            else:
                                population.append(self.df_pop[age_group_item].sum())
                        else:
                            if geschlecht == "M":
                                population.append(
                                    self.df_pop_m.query(
                                        f"Bundesland == '{state_series}'"
                                    )[age_group_item].values[0]
                                )
                            elif geschlecht == "W":
                                population.append(
                                    self.df_pop_w.query(
                                        f"Bundesland == '{state_series}'"
                                    )[age_group_item].values[0]
                                )
                            else:
                                population.append(
                                    self.df_pop.query(
                                        f"Bundesland == '{state_series}'"
                                    )[age_group_item].values[0]
                                )
            else:
                for _, gender_item in geschlecht.iteritems():
                    if state_series == "Alle":
                        if gender_item == "M":
                            population.append(self.df_pop_m[age_group].sum())
                        elif gender_item == "W":
                            population.append(self.df_pop_w[age_group].sum())
                        else:
                            population.append(self.df_pop[age_group].sum())
                    else:
                        if gender_item == "M":
                            population.append(
                                self.df_pop_m.query(f"Bundesland == '{state_series}'")[
                                    age_group
                                ].values[0]
                            )
                        elif gender_item == "W":
                            population.append(
                                self.df_pop_w.query(f"Bundesland == '{state_series}'")[
                                    age_group
                                ].values[0]
                            )
                        else:
                            population.append(
                                self.df_pop.query(f"Bundesland == '{state_series}'")[
                                    age_group
                                ].values[0]
                            )

        return population

    def select_state_week_data(self, altersgruppe, geschlecht, kategorie):
        """select infection cases"""

        if kategorie == "Hospitalisierung":
            selected_altersgruppe = {"gesamt": "A00+"}.get(altersgruppe, altersgruppe)
            return (
                self.hospitalisierung.query(f"Bundesland != 'Bundesgebiet'")
                .query(f"Altersgruppe == '{selected_altersgruppe}'")
                .rename(
                    columns={
                        "7T_Hospitalisierung_Faelle": "cases",
                        "7T_Hospitalisierung_Inzidenz": "inzidenz",
                    }
                )
                .assign(
                    population=lambda x: self.get_agegroup_population(
                        x.Bundesland, f"{altersgruppe}", "Alle"
                    )
                )
            )
        else:
            if altersgruppe == "gesamt":
                selected = self.df_rki_raw  # check if should use copy()
            else:
                selected = self.df_rki_raw.query(f"Altersgruppe == '{altersgruppe}'")

            if geschlecht == "Alle":
                selected = selected.groupby(
                    ["Bundesland", "week"], as_index=False
                ).sum()
            else:
                selected = (
                    selected.query(f"Geschlecht == '{geschlecht}'")
                    .groupby(["Bundesland", "week"], as_index=False)
                    .sum()
                )

            selected = selected.assign(
                population=lambda x: self.get_agegroup_population(
                    x.Bundesland, f"{altersgruppe}", f"{geschlecht}"
                )
            ).assign(ratio=lambda x: x.AnzahlTodesfall / x.AnzahlFall * 100)

            if kategorie == "Infektionsfälle":
                return selected.assign(
                    inzidenz=lambda x: x.AnzahlFall * 100000 / x.population
                )
            else:
                return selected.assign(
                    inzidenz=lambda x: x.AnzahlTodesfall * 100000 / x.population
                )

    def select_state_agegroup_data(self, geschlecht, meldewoche, kategorie):
        """select infection cases"""

        if kategorie == "Hospitalisierung":
            if meldewoche == "Alle":
                return (
                    self.hospitalisierung.query("Altersgruppe != 'A00+'")
                    .query(f"Bundesland != 'Bundesgebiet'")
                    .rename(columns={"7T_Hospitalisierung_Faelle": "AnzahlFall"})
                    .groupby(["Bundesland", "Altersgruppe"], as_index=False)
                    .agg(cases=("AnzahlFall", "sum"))
                    .assign(
                        population=lambda x: self.get_agegroup_population(
                            x.Bundesland, x.Altersgruppe, "Alle"
                        )
                    )
                    .assign(inzidenz=lambda x: x.cases * 100000 / x.population)
                )
                return
            else:
                return (
                    self.hospitalisierung.query("Altersgruppe != 'A00+'")
                    .query(f"week == '{meldewoche}'")
                    .query(f"Bundesland != 'Bundesgebiet'")
                    .assign(
                        population=lambda x: self.get_agegroup_population(
                            x.Bundesland, x.Altersgruppe, "Alle"
                        )
                    )
                    .rename(
                        columns={
                            "7T_Hospitalisierung_Inzidenz": "inzidenz",
                            "7T_Hospitalisierung_Faelle": "cases",
                        }
                    )
                )
        else:
            if meldewoche == "Alle":
                selected = self.df_rki_raw.query("Altersgruppe != 'unbekannt'")
            else:
                selected = self.df_rki_raw.query("Altersgruppe != 'unbekannt'").query(
                    f"week == '{meldewoche}'"
                )

            if geschlecht == "Alle":
                selected = selected.groupby(
                    ["Bundesland", "Altersgruppe"], as_index=False
                ).sum()
            else:
                selected = (
                    selected.query(f"Geschlecht == '{geschlecht}'")
                    .groupby(["Bundesland", "Altersgruppe"], as_index=False)
                    .sum()
                )

            selected = selected.assign(
                population=lambda x: self.get_agegroup_population(
                    x.Bundesland, x.Altersgruppe, f"{geschlecht}"
                )
            ).assign(ratio=lambda x: x.AnzahlTodesfall / x.AnzahlFall * 100)

            if kategorie == "Infektionsfälle":
                return selected.assign(
                    inzidenz=lambda x: x.AnzahlFall * 100000 / x.population
                )
            else:
                return selected.assign(
                    inzidenz=lambda x: x.AnzahlTodesfall * 100000 / x.population
                )

    def select_state_gender_data(self, altersgruppe, meldewoche, kategorie):
        """select infection cases"""

        if meldewoche == "Alle":
            selected = self.df_rki_raw
        else:
            selected = self.df_rki_raw.query(f"week == '{meldewoche}'")
        # check if should use copy()
        if altersgruppe == "gesamt":
            selected = selected.groupby(
                ["Bundesland", "Geschlecht"], as_index=False
            ).sum()
        else:
            selected = (
                selected.query(f"Altersgruppe == '{altersgruppe}'")
                .groupby(["Bundesland", "Geschlecht"], as_index=False)
                .sum()
            )

        selected = selected.assign(
            population=lambda x: self.get_agegroup_population(
                x.Bundesland, f"{altersgruppe}", x.Geschlecht
            )
        ).assign(ratio=lambda x: x.AnzahlTodesfall / x.AnzahlFall * 100)

        if kategorie == "Infektionsfälle":
            return selected.assign(
                inzidenz=lambda x: x.AnzahlFall * 100000 / x.population
            )
        else:
            return selected.assign(
                inzidenz=lambda x: x.AnzahlTodesfall * 100000 / x.population
            )

    def select_week_agegroup_data(self, geschlecht, bundesland, kategorie):
        """select infection cases"""

        if kategorie == "Hospitalisierung":
            selected_state = {"Alle": "Bundesgebiet"}.get(bundesland, bundesland)

            return (
                self.hospitalisierung.query("Altersgruppe != 'A00+'")
                .query(f"Bundesland == '{selected_state}'")
                .rename(columns={"7T_Hospitalisierung_Faelle": "AnzahlFall"})
                .groupby(["week", "Altersgruppe"], as_index=False)
                .agg(cases=("AnzahlFall", "sum"))
                .assign(
                    population=lambda x: self.get_agegroup_population(
                        f"{bundesland}", x.Altersgruppe, "Alle"
                    )
                )
                .assign(inzidenz=lambda x: x.cases * 100000 / x.population)
            )

        else:
            if bundesland == "Alle":
                selected = self.df_rki_raw.query("Altersgruppe != 'unbekannt'")
            else:
                selected = self.df_rki_raw.query(f"Bundesland == '{bundesland}'").query(
                    "Altersgruppe != 'unbekannt'"
                )

            if geschlecht == "Alle":
                selected = selected.groupby(
                    ["week", "Altersgruppe"], as_index=False
                ).sum()
            else:
                selected = (
                    selected.query(f"Geschlecht == '{geschlecht}'")
                    .groupby(["week", "Altersgruppe"], as_index=False)
                    .sum()
                )

            selected = selected.assign(
                population=lambda x: self.get_agegroup_population(
                    f"{bundesland}", x.Altersgruppe, f"{geschlecht}"
                )
            ).assign(ratio=lambda x: x.AnzahlTodesfall / x.AnzahlFall * 100)

            if kategorie == "Infektionsfälle":
                return selected.assign(
                    inzidenz=lambda x: x.AnzahlFall * 100000 / x.population
                )
            else:
                return selected.assign(
                    inzidenz=lambda x: x.AnzahlTodesfall * 100000 / x.population
                )

    def select_week_gender_data(self, altersgruppe, bundesland, kategorie):
        """select infection cases"""

        if bundesland == "Alle":
            selected = self.df_rki_raw
        else:
            selected = self.df_rki_raw.query(f"Bundesland == '{bundesland}'")

        if altersgruppe == "gesamt":
            selected = selected.groupby(["week", "Geschlecht"], as_index=False).sum()
        else:
            selected = (
                selected.query(f"Altersgruppe == '{altersgruppe}'")
                .groupby(["week", "Geschlecht"], as_index=False)
                .sum()
            )

        selected = selected.assign(
            population=lambda x: self.get_agegroup_population(
                f"{bundesland}", f"{altersgruppe}", x.Geschlecht
            )
        ).assign(ratio=lambda x: x.AnzahlTodesfall / x.AnzahlFall * 100)

        if kategorie == "Infektionsfälle":
            return selected.assign(
                inzidenz=lambda x: x.AnzahlFall * 100000 / x.population
            )
        else:
            return selected.assign(
                inzidenz=lambda x: x.AnzahlTodesfall * 100000 / x.population
            )

    def select_agegroup_gender_data(self, meldewoche, bundesland, kategorie):
        """select infection cases"""

        if bundesland == "Alle":
            selected = self.df_rki_raw
        else:
            selected = self.df_rki_raw.query(f"Bundesland == '{bundesland}'")

        if meldewoche == "Alle":
            pass
        else:
            selected = selected.query(f"week == '{meldewoche}'")

        selected = (
            selected.query("Altersgruppe != 'unbekannt'")
            .groupby(["Altersgruppe", "Geschlecht"], as_index=False)
            .sum()
            .assign(
                population=lambda x: self.get_agegroup_population(
                    f"{bundesland}", x.Altersgruppe, x.Geschlecht
                )
            )
            .assign(ratio=lambda x: x.AnzahlTodesfall / x.AnzahlFall * 100)
        )

        if kategorie == "Infektionsfälle":
            return selected.assign(
                inzidenz=lambda x: x.AnzahlFall * 100000 / x.population
            )
        else:
            return selected.assign(
                inzidenz=lambda x: x.AnzahlTodesfall * 100000 / x.population
            )

    def get_correlation_data(self, bundesland, week_range, w1, w2, w3, shift_weeks):

        from_week = week_range[0].strftime("%Y-%W")
        until_week = week_range[1].strftime("%Y-%W")

        category_ranges = [
            int(w1[0].strftime("%Y%W")),
            int(w2[0].strftime("%Y%W")),
            int(w2[1].strftime("%Y%W")),
            int(w3[1].strftime("%Y%W")),
        ]

        labels = ["w1", "w2", "w3"]

        if bundesland == "Alle":
            selected = (
                self.df_rki_raw.groupby(["week"], as_index=False)
                .sum()
                .query(f"(week >= '{from_week}') & (week <= '{until_week}')")
                .assign(ratio=lambda x: (x.AnzahlTodesfall / x.AnzahlFall) * 100)
                .assign(week_int=lambda x: x["week"].str.replace("-", "").astype(int))
                .sort_values(by=["AnzahlFall"])
            )
        else:
            selected = (
                self.df_rki_raw.query(f"Bundesland == '{bundesland}'")
                .groupby(["week"], as_index=False)
                .sum()
                .query(f"(week >= '{from_week}') & (week <= '{until_week}')")
                .assign(ratio=lambda x: (x.AnzahlTodesfall / x.AnzahlFall) * 1000)
                .assign(week_int=lambda x: x["week"].str.replace("-", "").astype(int))
                .sort_values(by=["AnzahlFall"])
            )

        selected["category"] = pd.cut(
            selected.week_int, category_ranges, right=False, labels=labels
        )

        selected["AnzahlTodesfall"] = selected["AnzahlTodesfall"].shift(-shift_weeks)

        return selected
