import streamlit as st
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta
from PIL import Image 
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
#import locale

#locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
image = Image.open('utilization_image.png')
st.image(image)

st.title('Client Utilization Data')
utilization_data = st.session_state['utilization_data']
active_enrollees = st.session_state['active_enrollees']

policyno = st.sidebar.text_input('Client Policy Number')
st.sidebar.button(label='Submit')

# if 'policy' not in st.session_state:
#     st.session_state['policy'] = None

# if policyno is not None:
#     st.session_state['policy'] = policyno
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

def display_utilization_data(policy):
    if not policy.isdigit():
        st.write('Enter a valid PolicyNo for the Client')  
        return
    policy = int(policy) 

    if policy not in utilization_data['PolicyNo'].values:
        st.write('No data found for the given policy number')
## Range selector
    start_date = pd.to_datetime(st.sidebar.date_input('Start Date',min_value=dt.datetime.now().date()-relativedelta(years=1)))
    end_date = pd.to_datetime(st.sidebar.date_input('End Date',max_value=dt.datetime.now().date()))
    benefit = st.selectbox(label='Select Benefit', options=('All','Consultation','Drugs','Chronic Disease','Optical', 'Dental', 'Lab Investigation', 'Annual Health Check', 'Surgery', 'Maternity', 'Others'))

    client_data = utilization_data.loc[
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date) &
            (utilization_data['PolicyNo'] == policy) &
            (utilization_data['New Approval Status'] == 'APPROVED'),
            ['AvonPaCode','Client','EnrolleeName','Sex','Relation', 'MemberNo','PlanName','ProviderName', 'State', 'CaseManager', 'EncounterDate', 'Benefit','Diagnosis', 'Speciality', 'ServiceDescription', 'ApprovedPAAmount' ]
            ]
    if benefit == 'All':
        data = client_data
    elif benefit == 'Consultation':
        data = client_data.loc[client_data['Benefit'].isin(consultation)]
    elif benefit == 'Chronic Disease':
        data = client_data.loc[client_data['Benefit']== 'CHRONIC DISEASE MANAGEMENT']
    elif benefit == 'Optical':
        data = client_data.loc[client_data['Benefit'].isin(optical)]
    elif benefit == 'Dental':
        data = client_data.loc[client_data['Benefit'].isin(dental)]
    elif benefit == 'Surgery':
        data = client_data.loc[client_data['Benefit'].isin(surgery)]
    elif benefit == 'Lab Investigation':
        data = client_data.loc[client_data['Benefit'].isin(lab_investigation)]
    elif benefit == 'Annual Health Check':
        data = client_data.loc[client_data['Benefit'].isin(health_check)]
    elif benefit == 'Maternity':
        data = client_data.loc[client_data['Benefit'].isin(maternity)]
    elif benefit == 'Drugs':
        data = client_data.loc[client_data['Benefit'].isin(drugs)]
    else:
        data = client_data[~client_data['Benefit'].isin(others)]
    try:
        client_pa_value = int(data['ApprovedPAAmount'].sum())
        client_pa_value = '#' + '{:,}'.format(client_pa_value) 
        client_pa_count = data['AvonPaCode'].nunique()
        client_pa_count = '{:,}'.format(client_pa_count)
        client_member_count = data['MemberNo'].nunique()
        client_member_count = '{:,}'.format(client_member_count)
        client_name = client_data['Client'].values[0]
    
        active_lives = active_enrollees.loc[
        active_enrollees['PolicyNo'] == policy,
        'MemberNo'
        ].nunique()
        active_lives = '{:,}'.format(active_lives)
    except IndexError:
        st.write('No Data Available for this date range or Benefit')

    if len(data) > 0:
        st.subheader(client_name + ' utilization between ' + str(start_date.date()) + ' and ' + str(end_date.date()))
        col1, col2 = st.columns(2)
        col1.metric(label = 'Total PA Value', value = client_pa_value)
        col2.metric(label = 'Total PA Count', value = client_pa_count)

        col3, col4 = st.columns(2)
        col3.metric(label='Number of Active Lives', value=active_lives)
        col4.metric(label = 'Number of Enrollees who Accessed Care', value = client_member_count)
        data['MemberNo'] = data['MemberNo'].astype(str)
        plan_agg = data.groupby('PlanName').agg({'ApprovedPAAmount':'sum', 'AvonPaCode':'nunique', 'MemberNo':'nunique'}).sort_values(by='ApprovedPAAmount',ascending=False).__round__(2)
        plan_agg = plan_agg.reset_index()
        data = data.set_index('AvonPaCode')
        st.dataframe(plan_agg)
        st.dataframe(data)

        st.download_button(
            label='Download data as Excel File',
            data=data.to_csv().encode('utf-8'),
            file_name=str(client_name + '.csv'),
            mime='text/csv',
            )
    else:
        st.write('No data found for the given policy number and date range')
        return 


display_utilization_data(policyno)

