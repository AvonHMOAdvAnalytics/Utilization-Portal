import streamlit as st
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta
from PIL import Image
#import locale

#locale.setlocale(locale.LC_ALL, 'en_US')
image = Image.open('utilization_image.png')
st.image(image)

st.title('Provider Utilization Data')
utilization_data = st.session_state['utilization_data']
active_enrollees = st.session_state['active_enrollees']

providerno = st.sidebar.text_input('Provider Number')
st.sidebar.button(label='Submit')

# if 'provider' not in st.session_state:
#     st.session_state['provider'] = None

# if providerno is not None:
#     st.session_state['provider'] = providerno
health_check = ['ANNUAL HEALTH CHECK ADVANCED', 'ANNUAL HEALTH CHECK BASIC', 'ANNUAL HEALTH CHECK COMPREHENSIVE', 'ANNUAL HEALTH CHECK PRINCIPAL ONLY']
consultation = ['CONSULTATION GENERAL', 'NUTRITIONIST AND DIETICIAN CONSULTATION', 'CONSULTATION SPECIALIST', 'PRE ADMISSION AND POST DISCHARGE FOLLOWUP CONSULTATION (GENERAL CONSULT)',
                 'PRE ADMISSION AND POST DISCHARGE FOLLOWUP CONSULTATION (SPECIALIST CONSULT)', 'PRE ADMISSION AND POST DISCHARGE FOLLOWUP CONSULT GP AND SPECIALIST']
dental = ['BUPA DENTAL COMPREHENSIVE', 'DENTAL CARE BASIC','DENTAL CARE COMPREHENSIVE','DENTAL CARE ORTHODONTICS','DENTAL CARE RESTORATIVES DENTURES BRIDGES CROWNS AND IMPLANTS',
          'PRIMARY DENTAL CARE','SECONDARY DENTAL CARE']
optical = ['BUPA OPTICAL', 'BUPA OPTICAL AND OPHTHALMIC CARE', 'GLASSES CONTACT LENSES AND EYE TESTS', 'OPTICAL CARE EYE TEST AND FRAME AND LENSE',
            'OPTICAL CARE SIMPLE AND ACUTE', 'PRIMARY OPTICAL CARE']
lab_investigation = ['RADIOLOGY X RAYS CONTRAST ONLY', 'ADVANCED INVESTIGATIONS','ULTRASOUND SCANS','ADVANCED INVESTIGATIONS ECG ONLY',
                     'BASIC RADIOLOGICAL SERVICES X RAYS PLAIN AND CONTRAST ULTRASOUND ABDOMINAL AND PELVIC AND ECG ANDEEG','LAB INVESTIGATIONS',
                     'INFERTILITY INVESTIGATION','RADIOLOGY X RAYS PLAIN ONLY','FERTILITY OR INFERTILITY INVESTIGATIONS']
surgery = ['INTERMEDIATE SURGERY','MAJOR SURGERY','MINOR AND INTERMEDIATE SURGERIES', 'MINOR INTERMEDIATE AND MAJOR SURGERIES',
            'MINOR SURGERY','SURGERIES COMPREHENSIVE','SURGERY CONSUMABLES','TRANSPLANT SURGERIES']
maternity = ['MATERNITY AND POST NATAL CARE', 'NEONATAL CARE', 'ROUTINE IMMUNIZATIONS AND PEDIATRIC IMMUNIZATIONS']
drugs = ['POST DISCHARGE TAKE HOME PRESCRIBED DRUGS','PRESCRIBED DRUGS AND INFUSIONS']
others = ['ANNUAL HEALTH CHECK ADVANCED', 'ANNUAL HEALTH CHECK BASIC', 'ANNUAL HEALTH CHECK COMPREHENSIVE', 'ANNUAL HEALTH CHECK PRINCIPAL ONLY','CONSULTATION GENERAL',
           'NUTRITIONIST AND DIETICIAN CONSULTATION', 'CONSULTATION SPECIALIST', 'PRE ADMISSION AND POST DISCHARGE FOLLOWUP CONSULTATION (GENERAL CONSULT)',
           'PRE ADMISSION AND POST DISCHARGE FOLLOWUP CONSULTATION (SPECIALIST CONSULT)', 'PRE ADMISSION AND POST DISCHARGE FOLLOWUP CONSULT GP AND SPECIALIST',
           'BUPA DENTAL COMPREHENSIVE', 'DENTAL CARE BASIC','DENTAL CARE COMPREHENSIVE','DENTAL CARE ORTHODONTICS','DENTAL CARE RESTORATIVES DENTURES BRIDGES CROWNS AND IMPLANTS',
          'PRIMARY DENTAL CARE','SECONDARY DENTAL CARE','BUPA OPTICAL', 'BUPA OPTICAL AND OPHTHALMIC CARE', 'GLASSES CONTACT LENSES AND EYE TESTS', 'OPTICAL CARE EYE TEST AND FRAME AND LENSE',
            'OPTICAL CARE SIMPLE AND ACUTE', 'PRIMARY OPTICAL CARE','RADIOLOGY X RAYS CONTRAST ONLY', 'ADVANCED INVESTIGATIONS','ULTRASOUND SCANS','ADVANCED INVESTIGATIONS ECG ONLY', 
            'BASIC RADIOLOGICAL SERVICES X RAYS PLAIN AND CONTRAST ULTRASOUND ABDOMINAL AND PELVIC AND ECG ANDEEG','LAB INVESTIGATIONS','INFERTILITY INVESTIGATION',
            'RADIOLOGY X RAYS PLAIN ONLY','FERTILITY OR INFERTILITY INVESTIGATIONS','INTERMEDIATE SURGERY','MAJOR SURGERY','MINOR AND INTERMEDIATE SURGERIES', 
            'MINOR INTERMEDIATE AND MAJOR SURGERIES','MINOR SURGERY','SURGERIES COMPREHENSIVE','SURGERY CONSUMABLES','TRANSPLANT SURGERIES','MATERNITY AND POST NATAL CARE', 'NEONATAL CARE',
             'ROUTINE IMMUNIZATIONS AND PEDIATRIC IMMUNIZATIONS','POST DISCHARGE TAKE HOME PRESCRIBED DRUGS','PRESCRIBED DRUGS AND INFUSIONS','CHRONIC DISEASE MANAGEMENT']


def display_utilization_data(provider):
    # providerno = st.session_state['provider']
    if not provider.isdigit():
        st.write('Enter a valid Provider Number')
        return
    provider = int(provider)

    # if provider not in utilization_data['ProviderNo'].values:
    #     st.write('No data found for the given policy number')

 ## Range selector
    start_date = pd.to_datetime(st.sidebar.date_input('Start Date',min_value=dt.datetime.now().date()-relativedelta(years=1)))
    end_date = pd.to_datetime(st.sidebar.date_input('End State',max_value=dt.datetime.now().date()))
    benefit = st.selectbox(label='Select Benefit', options=('All','Consultation','Drugs','Chronic Disease','Optical', 'Dental', 'Lab Investigation', 'Wellness', 'Surgery', 'Maternity', 'Others'))

    provider_data = utilization_data.loc[
            (utilization_data['ProviderNo'] == provider) &
            (utilization_data['PAIssueDate'] >= start_date) &
            (utilization_data['PAIssueDate'] <= end_date) &
            (utilization_data['New Approval Status'] == 'APPROVED'),
            ['AvonPaCode','Client','EnrolleeName','Sex','Relation', 'MemberNo','PlanName','ProviderName', 'State', 'ProviderManager', 'EncounterDate','PAIssueDate', 'Benefit','Diagnosis', 'Speciality', 'ServiceDescription', 'ApprovedPAAmount' ]
            ]

    if benefit == 'All':
        data = provider_data
    elif benefit == 'Consultation':
        data = provider_data.loc[provider_data['Benefit'].isin(consultation)]
    elif benefit == 'Chronic Disease':
        data = provider_data.loc[provider_data['Benefit']== 'CHRONIC DISEASE MANAGEMENT']
    elif benefit == 'Optical':
        data = provider_data.loc[provider_data['Benefit'].isin(optical)]
    elif benefit == 'Dental':
        data = provider_data.loc[provider_data['Benefit'].isin(dental)]
    elif benefit == 'Surgery':
        data = provider_data.loc[provider_data['Benefit'].isin(surgery)]
    elif benefit == 'Lab Investigation':
        data = provider_data.loc[provider_data['Benefit'].isin(lab_investigation)]
    elif benefit == 'Wellness':
        data = provider_data.loc[provider_data['Benefit'].isin(health_check)]
    elif benefit == 'Maternity':
        data = provider_data.loc[provider_data['Benefit'].isin(maternity)]
    elif benefit == 'Drugs':
        data = provider_data.loc[provider_data['Benefit'].isin(drugs)]
    else:
        data = provider_data[~provider_data['Benefit'].isin(others)]
    try:
        provider_pa_value = int(data['ApprovedPAAmount'].sum())
        provider_pa_value = '#' + '{:,}'.format(provider_pa_value) 
    
        provider_pa_count = data['AvonPaCode'].nunique()
        provider_pa_count = '{:,}'.format(provider_pa_count)
        provider_member_count = data['MemberNo'].nunique()
        provider_member_count = '{:,}'.format(provider_member_count)
        provider_name = data['ProviderName'].values[0]
        provider_class = utilization_data.loc[utilization_data['ProviderNo'] == provider, 'ProviderClass'].values[0]
   
        active_lives = active_enrollees.loc[
            active_enrollees['PrimaryProviderNo'] == provider,
            'MemberNo'
            ].nunique()
        active_lives = '{:,}'.format(active_lives)
    except IndexError:
        st.write('No Data Available for this date range or Benefit')

    if len(provider_data) > 0:
        try:  
            st.subheader(provider_name + ' utilization between ' + str(start_date.date()) + ' and ' + str(end_date.date()))
            col1, col2 = st.columns(2)
            col1.metric(label = 'Total PA Value', value = provider_pa_value)
            col2.metric(label = 'Total PA Count', value = provider_pa_count)

            col3, col4 = st.columns(2)
            col3.metric(label='Number of Active Lives', value=active_lives)
            col4.metric(label = 'Number of Enrollees who Accessed Care', value = provider_member_count)

            st.metric(label='Provider Class', value=provider_class)
            utilization_data['MemberNo'] = utilization_data['MemberNo'].astype(str)

            data['MemberNo'] = data['MemberNo'].astype(str)
            client_agg = data.groupby('Client').agg({'ApprovedPAAmount':'sum','AvonPaCode':'nunique','MemberNo':'nunique'}).sort_values(by='ApprovedPAAmount',ascending=False).__round__(2)
            client_agg = client_agg.rename(columns={'ApprovedPAAmount':'Total PA Amount', 'AvonPaCode':'PA Generated', 'MemberNo':'No. of Enrollees'})
            client_agg = client_agg.reset_index()
            data = data.set_index('AvonPaCode')
            st.dataframe(client_agg.head(10))
            st.dataframe(data)
        


            st.download_button(
            label= 'Download data as Excel File',
            data = data.to_csv().encode('utf-8'),
            file_name=str(provider_name + '.csv'),
            mime='test/csv',
            )
        except IndexError:
            st.write('No Data Available for this date range or Benefit')

    else:
        st.write('No data found for the given provider number and date range')
        return
    
display_utilization_data(providerno)

