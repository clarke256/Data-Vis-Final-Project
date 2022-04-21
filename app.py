import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from vega_datasets import data

counties = alt.topo_feature(data.us_10m.url, 'counties')

gd = pd.read_csv('gender.csv')
conversion = pd.read_csv('country_codes.csv')
conversion = conversion.drop_duplicates('alpha-3')
conversion.index = conversion['alpha-3']
variables = [
    'Country Name',
    'Country Code',
    'Year',
    'average_value_Adolescent fertility rate (births per 1,000 women ages 15-19)',
    'average_value_Fertility rate, total (births per woman)',
    'average_value_Life expectancy at birth, female (years)',
    'average_value_Life expectancy at birth, male (years)',
    'average_value_Mortality rate, adult, female (per 1,000 female adults)',
    'average_value_Mortality rate, adult, male (per 1,000 male adults)',
    'average_value_Survival to age 65, female (% of cohort)',
    'average_value_Survival to age 65, male (% of cohort)'
]
rename = [
    'Country Name',
    'Country Code',
    'Year',
    'Adolescent fertility rate',
    'Fertility rate total',
    'Life expectancy at birth (female)',
    'Life expectancy at birth (male)',
    'Mortality rate adult (female)',
    'Mortality rate adult (male)',
    'Survival to age 65 (female)',
    'Survival to age 65 (male)'
]
gd = gd[variables].dropna()
gd = gd[gd['Country Code'].isin(conversion.index)]
gd.columns = rename
gd['Life expectancy at birth ratio (female to male)'] = gd['Life expectancy at birth (female)'] / gd['Life expectancy at birth (male)']
gd['Mortality rate adult ratio (female to male)'] = gd['Mortality rate adult (female)'] / gd['Mortality rate adult (male)']
gd['Survival to age 65 ratio (female to male)'] = gd['Survival to age 65 (female)'] / gd['Survival to age 65 (male)']
gd['Life expectancy at birth'] = (gd['Life expectancy at birth (female)'] + gd['Life expectancy at birth (male)']) / 2
gd['id'] = [int(conversion['country-code'].loc[c]) for c in gd['Country Code']]
gd['Region'] = [conversion['region'].loc[c] for c in gd['Country Code']]
rename += ['Life expectancy at birth ratio (female to male)',
           'Mortality rate adult ratio (female to male)',
           'Survival to age 65 ratio (female to male)',
           'Life expectancy at birth']

gdp = pd.read_csv('gdp_per_capita.csv')
# print(gdp['Country Code'])
# print(conversion.index)
gdp['id'] = [int(conversion['country-code'].loc[c]) if c in conversion.index else np.nan for c in gdp['Country Code']]
gdp.index = gdp['id']

countries = alt.topo_feature(data.world_110m.url, 'countries')

st.title('CSE 5544 Final Project')

st.header("Geographic Heatmap")

st.subheader("Choose Year:")
year = st.slider("year", 1960, 2019, 1990)
gd_ = gd[gd['Year'] == year]
gd_.index = gd_['id']
gd_['GDP Per Capita'] = gdp[str(year)].loc[gd_.index]

mp = alt.Chart(countries).mark_geoshape().transform_lookup(
    lookup='id',
    from_=alt.LookupData(gd_, key='id', fields=['Life expectancy at birth']),
).encode(
    color=alt.Color('Life expectancy at birth:Q', scale=alt.Scale(scheme='viridis'))
).properties(
    width=800,
    height=400
).project('equirectangular')

back = alt.Chart(countries).mark_geoshape(
    fill='lightgray',
    stroke='black'
).properties(
    width=800,
    height=400
).project('equirectangular')

st.altair_chart(back + mp, use_container_width=False)

mp = alt.Chart(gd_).mark_circle().encode(
    color='Region:N',
    x=alt.X('Life expectancy at birth (male)', scale=alt.Scale(domain=(20, 90))),
    y=alt.Y('Life expectancy at birth (female)', scale=alt.Scale(domain=(20, 90))),
    size=alt.Size('GDP Per Capita', scale=alt.Scale(type='log', domain=(100, 100000)))
).properties(
    width=800,
    height=400
)

line = pd.DataFrame({
    'Life expectancy at birth (male)': [20, 90],
    'Life expectancy at birth (female)':  [20, 90],
})

line = alt.Chart(line).mark_line(color= 'red').encode(
    x='Life expectancy at birth (male)',
    y='Life expectancy at birth (female)'
)

st.altair_chart(mp + line, use_container_width=False)

years = [str(x) for x in list(range(1960, 2020))]
mean_expectancy_per_year = lambda x: gd.loc[gd['Year'] == int(x)]['Life expectancy at birth'].dropna().mean()

bar_df = pd.DataFrame({
    'Year': years,
    'Avg GDP Per Capita': gdp[years].mean(),
    'Avg Life expectancy at birth': np.vectorize(mean_expectancy_per_year)(years)
})

bar = alt.Chart(bar_df).mark_bar(color='#5276A7').encode(
    x=alt.X('Year:T'),
    y=alt.Y('Avg GDP Per Capita:Q', axis=alt.Axis(titleColor='#5276A7'), scale=alt.Scale(type='log', domain=(100, 100000))),
)

line = alt.Chart(bar_df).mark_line(color='#F18727').encode(
    x=alt.X('Year:T'),
    y=alt.Y('Avg Life expectancy at birth:Q', axis=alt.Axis(titleColor='#F18727'), scale=alt.Scale(domain=(40, 80)))
)

chart = alt.layer(bar, line).resolve_scale(y='independent').properties(
    width=800,
    height=400
)
st.altair_chart(chart, use_container_width=False)