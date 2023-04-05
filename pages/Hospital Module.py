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


@st.cache(suppress_st_warning=True)
def display_utilization_data():
    try:
        providerno = st.sidebar.text_input('Provider Number')
        provider = int(providerno)
    except ValueError:
        st.write('Enter a valid integer for the Provider No')
        return
 ## Range selector
    start_date = pd.to_datetime(st.sidebar.date_input('Start Date',min_value=dt.datetime.now().date()-relativedelta(years=1)))
    end_date = pd.to_datetime(st.sidebar.date_input('End Date',max_value=dt.datetime.now().date()))

    try:
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
                ].reset_index(drop=True)
    except IndexError:
        st.write('No data found for the given provider number')
        return

    if providerno is not None and len(provider_data) > 0:  
        st.subheader(provider_name + ' utilization between ' + str(start_date.date()) + ' and ' + str(end_date.date()))
        st.metric(label = 'Total PA Value', value = provider_pa_value)
        st.metric(label = 'Total PA Count', value = provider_pa_count)
        st.metric(label = 'Number of Enrollees who Accessed Care', value = provider_member_count)
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
    
display_utilization_data()
