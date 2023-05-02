import streamlit as st
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta
from PIL import Image
import locale

locale.setlocale(locale.LC_ALL, 'en_US')
image = Image.open('utilization_image.png')
st.image(image)

st.title('Hospital Utilization Data')
utilization_data = st.session_state['utilization_data']
active_enrollees = st.session_state['active_enrollees']

providerno = st.sidebar.text_input('Provider Number')
st.sidebar.button(label='Submit')

# if 'provider' not in st.session_state:
#     st.session_state['provider'] = None

# if providerno is not None:
#     st.session_state['provider'] = providerno

def display_utilization_data(provider):
    # providerno = st.session_state['provider']
    if not provider.isdigit():
        st.write('Enter a valid integer for Provider Number')
        return
    provider = int(provider)
 ## Range selector
    start_date = pd.to_datetime(st.sidebar.date_input('Start Date',min_value=dt.datetime.now().date()-relativedelta(years=1)))
    end_date = pd.to_datetime(st.sidebar.date_input('End State',max_value=dt.datetime.now().date()))

    provider_pa_value = utilization_data.loc[
            (utilization_data['ProviderNo'] == provider) &
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date),
            'ApprovedPAAmount'].sum()
    provider_pa_value = '#' + locale.format_string('%d', provider_pa_value, grouping=True)
    provider_pa_count = utilization_data.loc[
            (utilization_data['ProviderNo'] == provider) &
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date),
            'AvonPACode'].nunique()
    provider_pa_count = locale.format_string('%d',provider_pa_count,grouping=True)
    provider_member_count = utilization_data.loc[
            (utilization_data['ProviderNo'] == provider) &
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date),
            'MemberNo'].nunique()
    provider_member_count = locale.format_string('%d',provider_member_count,grouping=True)
    provider_name = utilization_data.loc[utilization_data['ProviderNo'] == provider, 'Hospital'].values[0]
    provider_data = utilization_data.loc[
                (utilization_data['EncounterDate'] >= start_date) &
                (utilization_data['EncounterDate'] <= end_date) &
                (utilization_data['ProviderNo'] == provider),
                ['AvonPACode','MemberName','MemberNo','PlanName','Client', 'EncounterDate', 'Benefits', 'Speciality', 'ServiceDescription', 'ApprovedPAAmount' ]
                ].set_index('AvonPACode')
    
    active_lives = active_enrollees.loc[
        active_enrollees['PrimaryProviderNo'] == provider,
        'MemberNo'
    ].nunique()

    if provider_name is not None and len(provider_data) > 0:  
        st.subheader(provider_name + ' utilization between ' + str(start_date.date()) + ' and ' + str(end_date.date()))
        col1, col2 = st.columns(2)
        col1.metric(label = 'Total PA Value', value = provider_pa_value)
        col2.metric(label = 'Total PA Count', value = provider_pa_count)

        col3, col4 = st.columns(2)
        col3.metric(label='Number of Active Lives', value=active_lives)
        col4.metric(label = 'Number of Enrollees who Accessed Care', value = provider_member_count)
        utilization_data['MemberNo'] = utilization_data['MemberNo'].astype(str)
        st.dataframe(provider_data)
        st.download_button(
            label= 'Download data as Excel File',
            data = provider_data.to_csv().encode('utf-8'),
            file_name=str(provider_name + '.csv'),
            mime='test/csv',
        )

    else:
        st.write('No data found for the given provider number and date range')
        return
    
display_utilization_data(providerno)

