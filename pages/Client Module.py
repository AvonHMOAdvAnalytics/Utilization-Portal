import streamlit as st
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta
from PIL import Image 
import locale

locale.setlocale(locale.LC_ALL, 'en_US')
image = Image.open('utilization_image.png')
st.image(image)

st.title('Client Utilization Data')
utilization_data = st.session_state['utilization_data']

policyno = st.sidebar.text_input('Client Policy Number')
st.sidebar.button(label='Submit')

if 'policy' not in st.session_state:
    st.session_state['policy'] = None

if policyno is not None:
    st.session_state['policy'] = policyno


def display_utilization_data(policy):
    if not policy.isdigit():
        st.write('Enter a valid integer for PolicyNo')  
        return
    policy = int(policy) 

    if policy not in utilization_data['PolicyNo'].values:
        st.write('No data found for the given policy number')
## Range selector
    start_date = pd.to_datetime(st.sidebar.date_input('Start Date',min_value=dt.datetime.now().date()-relativedelta(years=1)))
    end_date = pd.to_datetime(st.sidebar.date_input('End Date',max_value=dt.datetime.now().date()))

    client_pa_value = utilization_data.loc[
            (utilization_data['PolicyNo'] == policy) &
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date),
            'ApprovedPAAmount'].sum()
    client_pa_value = '#' + locale.format_string('%d', client_pa_value, grouping=True)
    client_pa_count = utilization_data.loc[
            (utilization_data['PolicyNo'] == policy) &
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date),
            'AvonPACode'].nunique()
    client_pa_count = locale.format_string('%d', client_pa_count, grouping=True)
    client_member_count = utilization_data.loc[
            (utilization_data['PolicyNo'] == policy) &
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date),
            :].index.nunique()
    client_member_count = locale.format_string('%d', client_member_count, grouping=True)
    client_name = utilization_data.loc[utilization_data['PolicyNo'] == policy, 'Client'].values[0]
    client_data = utilization_data.loc[
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date) &
            (utilization_data['PolicyNo'] == policy),
            ['AvonPACode','MemberName', 'MemberNo','PlanName','Hospital', 'EncounterDate', 'Benefits', 'Speciality', 'ServiceDescription', 'ApprovedPAAmount' ]
            ].set_index('AvonPACode')

    if client_name is not None and len(client_data) > 0:
        st.subheader(client_name + ' utilization between ' + str(start_date.date()) + ' and ' + str(end_date.date()))
        st.metric(label = 'Total PA Value', value = client_pa_value)
        st.metric(label = 'Total PA Count', value = client_pa_count)
        st.metric(label = 'Number of Enrollees who Accessed Care', value = client_member_count)
        st.dataframe(client_data)

        st.download_button(
            label='Download data as Excel File',
            data=client_data.to_csv().encode('utf-8'),
            file_name=str(client_name + '.csv'),
            mime='text/csv',
            )
    else:
        st.write('No data found for the given policy number and date range')
        return 
    

display_utilization_data(policyno)
