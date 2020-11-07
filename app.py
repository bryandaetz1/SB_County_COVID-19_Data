# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 19:32:47 2020

@author: bdaet
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#getting data
cases_by_age = pd.read_csv('https://raw.githubusercontent.com/bryandaetz1/SB_County_COVID-19_Data/master/CSV_Files/cases_by_age_11-7-20.csv')
cases_by_area = pd.read_csv('https://raw.githubusercontent.com/bryandaetz1/SB_County_COVID-19_Data/master/CSV_Files/cases_by_area_11-7-20.csv')
cases_by_gender = pd.read_csv('https://raw.githubusercontent.com/bryandaetz1/SB_County_COVID-19_Data/master/CSV_Files/cases_by_gender_11-7-20.csv')
ethnicity = pd.read_csv('https://raw.githubusercontent.com/bryandaetz1/SB_County_COVID-19_Data/master/CSV_Files/ethnicity_11-7-20.csv')
recovery_status = pd.read_csv('https://raw.githubusercontent.com/bryandaetz1/SB_County_COVID-19_Data/master/CSV_Files/recovery_status_11-7-20.csv')



#CLEANING DATA FOR CASES BY AGE DATAFRAME

#rename columns
cases_by_age.rename(columns = {'Number of Cases by Age':'Age',
                               'Federal Prisonin Lompoc':'Lompoc Federal Prison',
                               'Total(Community & Prison)':'Total'}, inplace = True)

#fix duplicate age groups
cases_by_age['Age'].replace({'70+3':'70+'}, inplace = True)

#creating new dataframe without age suppressed and pending age values for visualization
age_viz = cases_by_age[~cases_by_age['Age'].isin(['Age Suppressed','Pending'])]

#creating list of available dates to select for dashboard
available_dates = age_viz.Date.unique()

#creating list of available locations to select for dashboard
available_locations = age_viz.columns[2:5].to_list()



#CLEANING DATA FOR CASES BY AREA DATAFRAME

#creating new Area column to clean up Geographic Area descriptions
area_dict = {'SOUTH COUNTY UNINCORPORATED AREA includes communities of Montecito, Summerland and the City of Carpinteria':'South County Unincorporated Area',
             'CITY OF SANTA BARBARA and the unincorporated area of Mission Canyon':'Santa Barbara',
             'CITY OF GOLETA':'Goleta',
             'COMMUNITY OF ISLA VISTA':'Isla Vista',
             'UNINCORPORATED AREA OF THE GOLETA VALLEY AND GAVIOTA':'Goleta Valley/Gaviota',
             'SANTA YNEZ VALLEY including the Cities of Solvang & Buellton, and the communities of Santa Ynez, Los Alamos, Los Olivos and Ballard':'Santa Ynez Valley',
             'CITY OF LOMPOC and the communities of Mission Hills and Vandenberg Village':'Lompoc',
             'FEDERAL PRISON IN LOMPOC':'Federal Prison in Lompoc',
             'CITY OF SANTA MARIA':'Santa Maria',
             'COMMUNITY OF ORCUTT':'Orcutt',
             'UNINCORPORATED AREAS of Sisquoc, Casmalia, Garey,\xa0 Cuyama, New Cuyama, and the City of Guadalupe':'Other Unincorporated Areas',
             'Total**':'Total',
             'Total*':'Total'}

cases_by_area['Area'] = cases_by_area['Geographic Area'].replace(area_dict)

#cleaning up Daily Cases column and converting to numeric
cases_by_area['Daily Cases'] = cases_by_area['Daily Cases'].apply(lambda x: x[:-1] if '*' in str(x) else x)    #there are a few cases where the number was follwed by an asterisk, removing asterisks
cases_by_area['Daily Cases'] = cases_by_area['Daily Cases'].str.strip().replace('—',np.nan)   #changing missing values to null so they don't appear on graph 
cases_by_area['Daily Cases'] = pd.to_numeric(cases_by_area['Daily Cases'])     #converting to numeric

#converting Date column to pandas datetime format
cases_by_area['Date'] = pd.to_datetime(cases_by_area['Date'])

#creating new dataframe for visualizations
areas_to_plot = ['Lompoc',
                 'Isla Vista',
                 'Orcutt',
                 'Federal Prison in Lompoc',
                 'Goleta Valley/Gaviota',
                 'Goleta',
                 'Santa Barbara',
                 'Santa Ynez Valley',
                 'Santa Maria']

#dropping original Geographic Area column and filtering for specific areas
area_viz = cases_by_area[cases_by_area['Area'].isin(areas_to_plot)][cases_by_area.columns[1:]]    

#renaming columns
area_viz.rename({'Daily Cases':'New Cases',
                 'Total\xa0 Confirmed Cases':'Total Confirmed Cases',
                 'Recovered by Region':'Recovered Cases',
                 'Still infectious by Region':'Active Cases'},
                axis = 1,
                inplace = True)

#fixing outlier in Active Cases column for Lompoc, looks like an extra zero was added by mistake
area_viz.loc[(area_viz['Area'] == 'Lompoc') & (area_viz['Active Cases'] > 200), ['Active Cases']] = 22

#fixing outlier in Number of Deaths column for Santa Maria, looks like an extra 3 was added by mistake
area_viz.loc[(area_viz['Area'] == 'Santa Maria') & (area_viz['Number of Deaths'] > 300), ['Number of Deaths']] = 34

#getting list of inputs for radio items in dashboard
available_inputs = area_viz.columns[:5].to_list()



#CLEANING DATA FOR CASES BY GENDER DATAFRAME

#rename columns
cases_by_gender.rename(columns = {'Number of Cases by Gender':'Gender',
                                  'Federal Prisonin Lompoc':'Lompoc Federal Prison',
                                  ' Total\xa0 (Community & Prison)':'Total'}, inplace = True)

#creating new dataframe for visualizations
cases_by_gender['Gender'].replace({'Unknown':'Other'}, inplace = True)

gender_viz = cases_by_gender[cases_by_gender['Gender'].isin(['Male','Female','Other'])]

#calculating totals by date to calculate percentage of total for each gender
totals_community = gender_viz.groupby('Date')['Community'].agg('sum')
totals_prison = gender_viz.groupby('Date')['Lompoc Federal Prison'].agg('sum')
totals = gender_viz.groupby('Date')['Total'].agg('sum')

#creating new columns showing the case count as a percentage of the total
gender_viz['Percentage of Community Cases'] = gender_viz.apply(lambda x: round(((x.Community / totals_community[totals_community.index == x.Date].values[0]) * 100), 2), axis = 1)

gender_viz['Percentage of Prison Cases'] = gender_viz.apply(lambda x: round(((x['Lompoc Federal Prison'] / totals_prison[totals_prison.index == x.Date].values[0]) * 100), 2), axis = 1)

gender_viz['Percentage of Total Cases'] = gender_viz.apply(lambda x: round(((x.Total / totals[totals.index == x.Date].values[0]) * 100), 2), axis = 1)

#creating dictionary so that the function to create a visualization for the cases_by_gender data
# can be run with a single input across the entire dashboard
column_dict = {'Community':'Percentage of Community Cases',
               'Lompoc Federal Prison':'Percentage of Prison Cases',
               'Total':'Percentage of Total Cases'}



#CLEANING DATA FOR ETHNICITY DATAFRAME

#looks like some duplicate values are the result of extra whitespaces, removing extra whitespaces
ethnicity['RACE/ETHNICITY'] = ethnicity['RACE/ETHNICITY'].str.strip()

#cleaning up duplicate values in RACE/ETHNICITY column
value_dict = {
              'Asian, Non-Hispanic':'Asian',
              'Other, Non-Hispanic':'Other',
              'Native Hawaiian or Pacific Islander, Non-Hispanic':'Native Hawaiian or Pacific Islander',
              'American Indian/Native Alaskan, Non-Hispanic':'American Indian/Native Alaskan',
              'White, Non-Hispanic':'White',
              'Multiracial, Non-Hispanic':'Multiracial',
              'Black/African American, Non-Hispanic':'Black/African American',
              'Suppressed/Inmate':'Suppressed'
}

ethnicity['RACE/ETHNICITY'].replace(value_dict, inplace = True)

#creating new dataframe for visualizations
ethnicity_viz = ethnicity.loc[ethnicity['RACE/ETHNICITY'].isin(['White',                               #filtering based on values in race/ethnicity column
                                                         'American Indian/Native Alaskan',
                                                         'Asian',
                                                         'Multiracial',
                                                         'Hispanic/Latino',
                                                         'Native Hawaiian or Pacific Islander',
                                                         'Black/African American']),
                                                        ['RACE/ETHNICITY','Community','Federal Prison in Lompoc','Total(Community & Prison)','Date']]    #selecting only columns I'll need for visualization
                                           
#cleaning up column names
ethnicity_viz.rename({'RACE/ETHNICITY':'Ethnicity',
                      'Federal Prison in Lompoc':'Lompoc Federal Prison',
                      'Total(Community & Prison)':'Total'}, 
                     axis = 1, 
                     inplace = True)



#CLEANING DATA FOR RECOVERY STATUS DATAFRAME

#cleaning up recovery status values
recovery_status['Recovery Status'].replace({'Still Infectious Cases':'Active Cases', 
                                            'Active Cases*':'Active Cases'},
                                           inplace = True)

#cleaning up column names
recovery_status.rename({'Community ':'Community',
                        'Federal Prison in Lompoc':'Lompoc Federal Prison',
                        'Total(Community & Prison)':'Total'},
                       axis = 1,
                       inplace = True)

#getting subset of data
recovery = recovery_status[recovery_status['Recovery Status'].isin(['Active Cases','Recovered Cases'])]

#converting community column to numeric
recovery['Community'] = pd.to_numeric(recovery['Community'])






# LAYOUT FOR APP

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#dictionary of colors for app
#original background color was #111111
colors = {'background': '#18191A',
          'text':'#E4E6EB',
          'text2':'#B0B3BB',
          'paper_bgcolor':'#242526',
          'plot_bgcolor':'#242526'
          #'plot_bgcolor':'#22303C'
          }

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    
    html.Div([
        
        html.H1('Santa Barbara County COVID-19 Dashboard',
                style = {'textAlign':'center','color':colors['text']}),
            
        dcc.RadioItems(id = 'radio-items',
                       options = [{'label': i, 'value': i} for i in available_inputs],
                       value = 'Active Cases',
                       style = {'color': colors['text2']}),
            
        dcc.Graph(id = 'cases-by-region') #figure for graph will be determined by app callback
            
                                       
        ],
        
        style = {'backgroundColor':colors['background']}),
    
    
    html.Div([
        
        html.H2('Demographic Data Over Time',
                style = {'textAlign':'left','color':colors['text']})
        
        ],
        
        style = {'backgroundColor':colors['background']}),
    
    html.Div([
        
        html.Div([
            
            html.H3('Select a Date:',
                style = {'textAlign':'left','color':colors['text2']}),
        
            dcc.Dropdown(
                id = 'date-dropdown',
                options = [{'label': i, 'value': i} for i in available_dates],
                value = available_dates[0],
                style = {'color':'black'}
                ),
            
            html.H3('Select a Location:',
                style = {'textAlign':'left','color':colors['text2']}),
                    
            dcc.Dropdown(
                id = 'location-dropdown',
                options = [{'label': i, 'value': i} for i in available_locations],
                value = 'Community',
                style = {'color':'black'}
                ),
        
            dcc.Graph(id = 'cases-by-gender') #figure for graph will be determined by app callback
            
            ],
            
            style={'display':'inline-block',
                   'width':'35%',
                   'vertical-align':'top',
                   'backgroundColor':colors['background']
                   }),
        
        html.Div([
            
            dcc.Graph(id = 'cases-by-ethnicity'), #figure for graph will be determined by app callback
            
            dcc.Graph(id = 'cases-by-age') #figure for graph will be determined by app callback
            
            ],
            
            style={'display':'inline-block',
                   'width':'60%',
                   'backgroundColor':colors['background']})
        
        
        ])
    
        
    ],
    
    style = {'backgroundColor':colors['background']}
    
    )






# CALLBACK FUNCTIONS

#function to make region graph interactive
@app.callback(
    Output(component_id='cases-by-region', component_property='figure'),
    [Input(component_id='radio-items', component_property='value')])

#function to create lineplot that can be used for any of the columns in the area_viz dataframe
def create_line_plot(column_name):
  fig = px.line(area_viz,
              x = 'Date',
              y = column_name,
              #opacity = 0.7,
              title = column_name + ' by Region',
              template = 'plotly_dark',
              color = 'Area',
              color_discrete_sequence = px.colors.qualitative.Plotly)
  
  fig.update_layout(
      hovermode = 'closest',
      title_font_size = 24,
      font_family = 'Courier',    #setting font style and color globally, could also set locally by using a font dictionary for the legend or title_font_family/color for title
      font_color = 'white',
      legend = dict(
          orientation='h',
          yanchor='bottom',
          y=1.02,
          xanchor='left',
          x=0
          ),
      paper_bgcolor = colors['paper_bgcolor'],
      plot_bgcolor = colors['plot_bgcolor']
  )
                  
  return fig



@app.callback(
    Output(component_id='cases-by-age', component_property='figure'),
    [Input(component_id='date-dropdown', component_property='value'),
     Input(component_id='location-dropdown', component_property='value')])

#function to create age barplot
def create_age_barplot(date, column_name):
  fig = px.bar(age_viz[age_viz['Date'] == date],
               x = 'Age',
               y = column_name,
               range_y = [0,3750],   #enhancement would be to calculate this based on max from dataframe
               color = 'Age',
               opacity = 0.65,
               color_discrete_sequence = px.colors.qualitative.D3,
               template = 'plotly_dark',
               title = column_name + ' Cases by Age as of ' + date)
  
  fig.update_layout(
      hovermode = 'closest',
      font_family = 'Courier',
      font_color = 'white',
      title_font_size = 24,
      yaxis = dict(title = None),
      xaxis = dict(title = 'Age Group'),
      showlegend = False,
      paper_bgcolor = colors['paper_bgcolor'],
      plot_bgcolor = colors['plot_bgcolor']
  )
  

  return fig


@app.callback(
    Output(component_id='cases-by-gender', component_property='figure'),
    [Input(component_id='date-dropdown', component_property='value'),
     Input(component_id='location-dropdown', component_property='value')])

#function to create pie chart for gender data
def create_pie_chart(date, column_name):
  fig = px.pie(gender_viz[gender_viz['Date'] == date],
               values = column_dict[column_name],
               names = 'Gender',
               color = 'Gender',
               opacity = 0.65,
               template = 'plotly_dark',
               title = column_dict[column_name] + ' by<br>Gender as of ' + date,
               color_discrete_sequence = px.colors.qualitative.D3[7:])
               #color_discrete_sequence = ['7F7F7F','BCBD22','17BECF'])
  
  fig.update_layout(font_family = 'Courier',
                    font_color = 'white',
                    title_font_size = 24,
                    legend = dict(
                        orientation = 'h',
                        yanchor = 'bottom',
                        y = -0.2,
                        xanchor = 'left',
                        x = -0.2
                    ),
                    paper_bgcolor = colors['paper_bgcolor'],
                    plot_bgcolor = colors['plot_bgcolor'])

  return fig


@app.callback(
    Output(component_id='cases-by-ethnicity', component_property='figure'),
    [Input(component_id='date-dropdown', component_property='value'),
     Input(component_id='location-dropdown', component_property='value')])

#function to create barplot for ethnicity data
def create_ethnicity_barplot(date, column_name):
  fig = px.bar(ethnicity_viz[ethnicity_viz['Date'] == date],
               x = column_name,
               y = 'Ethnicity',
               opacity = 0.65,
               range_x = [0,6000], #enhancement would be to calculate this based on max from dataframe
               color = 'Ethnicity',
               orientation = 'h',
               template = 'plotly_dark',
               title = column_name + ' Cases by Ethnicity as of ' + date,
               color_discrete_sequence = px.colors.qualitative.D3)
               
  
  fig.update_layout(
      hovermode = 'closest',
      font_family = 'Courier',
      font_color = 'white',
      title_font_size = 24,
      xaxis = dict(title=None),
      yaxis = dict(title=None),
      showlegend = False,
      paper_bgcolor = colors['paper_bgcolor'],
      plot_bgcolor = colors['plot_bgcolor'])

  return fig



#function to return active cases for a given column and date
def active_cases(date, column_name):
  count = int(recovery.loc[(recovery['Recovery Status'] == 'Active Cases') & (recovery['Date'] == date), column_name].values)
  return count

#function to return recovered cases for a given column and date
def recovered_cases(date, column_name):
  count = int(recovery.loc[(recovery['Recovery Status'] == 'Recovered Cases') & (recovery['Date'] == date), column_name].values)
  return count

    

if __name__ == '__main__':
    app.run_server()