import streamlit as st
import pandas as pd
import pyodbc
import datetime as dt
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import bcrypt
import os

# st.set_page_config(page_title='After-Care Satisfaction Survey Portal', layout='wide', initial_sidebar_state='expanded')

conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
        +st.secrets['server2']
        +';DATABASE='
        +st.secrets['database2']
        +';UID='
        +st.secrets['username2']
        +';PWD='
        +st.secrets['password2']
        ) 

#assign credentials for the avon flex DB credentials

query = 'SELECT * from vw_tbl_AfterCareSurvey'

survey_data = pd.read_sql(query, conn)

#convert the memberno to string
survey_data['MemberNo'] = survey_data['MemberNo'].astype(str)

#created a calendar to enable users select a date
date = st.sidebar.date_input('Pick a PAIssue Date')

#display each encounter based on the date selected
st.subheader(f'Approved Encounters for {date}')
encounter = survey_data[survey_data['PAIssueDate'] == date]
encounter = encounter[['MemberNo', 'MemberName', 'AvonPaCode', 'ProviderName', 'ServiceDescription', 'MobileNo']].reset_index(drop=True)
#display the distinct encounters for the selected date in a select box
st.write(encounter)
encounter = encounter['MemberNo'].unique()
selected_encounter = st.selectbox('Select MemberNo', encounter)

#retrieve the following details for the selected encounter, MemberNo, MemberName, PAIssueDate, ProviderName, ServiceDescription, MobileNo, FinalApprovalStatus
encounter_details = survey_data[(survey_data['PAIssueDate'] == date) & (survey_data['MemberNo'] == selected_encounter)]
sel_memberno = encounter_details['MemberNo'].values[0]
sel_membername = encounter_details['MemberName'].values[0]
sel_providername = encounter_details['ProviderName'].values[0] 
#the service description has multiple rows, so we will concatenate them
sel_servicedescription = ', '.join(encounter_details['ServiceDescription'].values)
sel_mobileno = encounter_details['MobileNo'].values[0]

#display the details using the metric
st.metric(label='MemberName', value=sel_membername)
st.metric(label='ProviderName', value=sel_providername)
st.metric(label='MobileNo', value=sel_mobileno)

st.metric(label='ServiceDescription', value=sel_servicedescription)

#enable users to enter the satisfaction survey details
reachable = st.radio('Was the Enrollee Reachable?', ['Yes', 'No'])
if reachable == 'Yes':
    satisfied = st.radio('Was the Enrollee Satisfied?', ['Yes', 'No'])
    comments = st.text_area('Comments')
    resolvable = st.radio('Is the issue resolvable by the Contact Center?', ['Yes', 'No, Requires Escalation to Other Units', 'No, Requires Provider Intervention'])
    action_taken = st.selectbox('Action Taken', placeholder='Select an Action', index=None, options= ['Resolved', 'Escalated to Other Units', 'Escalated to Provider', 'Others'])
    if action_taken == 'Resolved':
        resolution = st.text_area('Resolution')
    elif action_taken == 'Escalated to Other Units':
        escalation = st.text_area('Escalation Details')
else:
    satisfied = None
    comments = st.selectbox('Reason for not being reachable', placeholder='Select a Reason', index=None, options= ['Wrong Number', 'Switched Off', 'Not Reachable', 'Reachable but did not pick', 'Picked but Unavailable', 'Others'])

submit = st.button('Submit')

# if submit:



