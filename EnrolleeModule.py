import streamlit as st
import pandas as pd
import pyodbc
from PIL import Image
import datetime as dt
import os



st.set_page_config(page_title= 'Enrollee Utilization',layout='wide', initial_sidebar_state='expanded')


#locale.setlocale(locale.LC_ALL, 'en_US')
image = Image.open('avonwhite.png')
st.image(image, use_column_width=False)

st.sidebar.title('Navigation')
options = st.sidebar.radio('Module', options=['Home Page', 'Enrollee Utilization Summary', 'Enrollee Plan Benefit Limit'])

query = 'SELECT PolicyNo\
            ,ClientName\
            ,[Policy Inception]\
            ,[Policy Expiry]\
            ,PlanType\
            ,MemberType\
            ,MemberNo\
            ,Name\
            ,PrimaryProviderNo\
            ,Gender\
            ,DATEDIFF(year,DOB,getdate()) MemberAge\
            ,State\
            ,PrimaryProviderName\
            ,Email\
            ,MobileNo\
             from [dbo].[tbl_MemberMasterView]'

query1 = 'SELECT distinct * from utilization_portal_data'


@st.cache_data(ttl = dt.timedelta(hours=24))
def get_data_from_sql():
    server = os.environ.get('server_name')
    database = os.environ.get('db_name')
    username = os.environ.get('db_username')
    password = os.environ.get('password')
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
        + server
        +';DATABASE='
        + database
        +';UID='
        + username
        +';PWD='
        + password
        )
    active_enrolees = pd.read_sql(query, conn)
    utilization_data = pd.read_sql(query1, conn)
    utilization_data['PAIssueDate'] = pd.to_datetime(utilization_data['PAIssueDate'])
    conn.close()
    return active_enrolees, utilization_data

active_enrollees, utilization_data = get_data_from_sql()

limit_df = pd.read_csv('Benefit_Limits.csv')

st.session_state['utilization_data'] = utilization_data
st.session_state['active_enrollees'] = active_enrollees



memberid = st.sidebar.text_input('Enrollee Member ID')
st.sidebar.button(label='Submit')



def display_member_utilization(mem_id):   
    if not mem_id.isdigit():
        st.write('Enter a valid MemberNo')
        return 
  
    mem_id = int(mem_id)

    if mem_id not in active_enrollees['MemberNo'].values:
        st.write('No data found for the given member number')
        return
    
    policy_start_date = pd.to_datetime(active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'Policy Inception'].iat[0])
    policy_end_date = pd.to_datetime(active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'Policy Expiry'].iat[0])

    member_pa_value = utilization_data.loc[
            (utilization_data['MemberNo'] == mem_id) &
            (utilization_data['PAIssueDate'] >= policy_start_date) &
            (utilization_data['PAIssueDate'] <= policy_end_date) &
            (utilization_data['New Approval Status'] == 'APPROVED'),
            'ApprovedPAAmount'].sum() 
    member_pa_value = '#' + '{:,}'.format(member_pa_value)       
    #member_pa_value = '#' + locale.format_string('%d', member_pa_value, grouping=True)
    membername = active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'Name'].iat[0]
    client = active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'ClientName'].iat[0]
    plan = active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'PlanType'].iat[0]
    membertype = active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'MemberType'].iat[0]
    memberage = active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'MemberAge'].iat[0]
    member_utilization = utilization_data.loc[
            (utilization_data['PAIssueDate'] >= policy_start_date) &
            (utilization_data['PAIssueDate'] <= policy_end_date) &
            (utilization_data['MemberNo'] == mem_id) &
            (utilization_data['New Approval Status'] == 'APPROVED'),
            ['AvonPaCode','ProviderName', 'EncounterDate','PAIssueDate', 'Benefit', 'Diagnosis', 'Speciality', 'ServiceDescription','State', 'CaseManager', 'ApprovedPAAmount' ]
        ].set_index('AvonPaCode')

    if membername is not None and options == 'Home Page':  
        #col1,col2= st.columns(2)
        st.metric(label = 'Enrollee Name', value = membername)
        st.metric(label = 'Enrollee Client', value = client)
        st.metric(label = 'Enrollee Plan', value = plan)
        st.metric(label = 'Total Utilization Within Current Policy', value=member_pa_value)

        col3, col4 = st.columns(2)
        col3.metric(label = 'Enrollee Age', value = memberage)
        col4.metric(label = 'Member Type', value = membertype)

        col5, col6 = st.columns(2)        
        col5.metric(label = 'Policy Inception', value = str(policy_start_date))
        col6.metric(label = 'PolicyExpiry', value = str(policy_end_date))
        
        # except IndexError:
        #     st.write("Enrollee not available")
    elif len(member_utilization) > 0 and options == 'Enrollee Utilization Summary':
        st.subheader('Utilization summary for ' + membername)
        utilization_summary = member_utilization.groupby('Benefit')['ApprovedPAAmount'].sum().__round__(2)
        st.dataframe(utilization_summary, use_container_width=True)
        st.subheader('Utilization details for '+ membername)
        st.dataframe(member_utilization,use_container_width=True)
    elif options == 'Enrollee Plan Benefit Limit':
        enrollee_benefit_limit = limit_df.loc[
                (limit_df['ClientName'] == client) &
                (limit_df['ClassName'] == plan)
            ]
        null_cols = enrollee_benefit_limit.columns[enrollee_benefit_limit.isnull().all()]
        enrollee_benefit_limit.drop(null_cols, axis = 1, inplace = True)
        enrollee_benefit_limit = enrollee_benefit_limit.iloc[:, 6:].reset_index(drop=True)
        enrollee_benefit_limit = enrollee_benefit_limit.to_dict('index')
        
        st.write(enrollee_benefit_limit)
        return

display_member_utilization(memberid)
