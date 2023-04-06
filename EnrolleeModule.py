import streamlit as st
import pandas as pd
import pyodbc
from PIL import Image
import datetime as dt
import locale


st.set_page_config(page_title= 'Enrollee Utilization',layout='wide', initial_sidebar_state='expanded')


locale.setlocale(locale.LC_ALL, 'en_US')
image = Image.open('avonwhite.png')
st.image(image, use_column_width=False)

st.sidebar.title('Navigation')
options = st.sidebar.radio('Module', options=['Home Page', 'Enrollee Utilization Summary', 'Enrollee Plan Benefit Limit'])


@st.cache_data(ttl = dt.timedelta(hours=24))
def get_data_from_sql(query):
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
        +st.secrets['server']
        +';DATABASE='
        +st.secrets['database']
        +';UID='
        +st.secrets['username']
        +';PWD='
        +st.secrets['password']
        )
    df = pd.read_sql(query, conn)
    conn.close()
    return df

query = 'SELECT PolicyNo\
            ,ClientName\
            ,[Policy Inception]\
            ,[Policy Expiry]\
            ,PlanType\
            ,MemberType\
            ,MemberNo\
            ,Name\
            ,Gender\
            ,DATEDIFF(year,DOB,getdate()) MemberAge\
            ,State\
            ,PrimaryProviderName\
            ,Email\
            ,MobileNo\
             from [dbo].[tbl_MemberMasterView]'
active_enrollees = get_data_from_sql(query=query)

query1 = 'SELECT * from vw_utilization_data'
utilization_data = get_data_from_sql(query=query1)
utilization_data['EncounterDate'] = pd.to_datetime(utilization_data['EncounterDate'])
limit_df = pd.read_csv('Benefit_Limits.csv')

st.session_state['utilization_data'] = utilization_data


def display_member_utilization():
    try:
        memberid = st.sidebar.text_input('Enrollee Member ID')
        memberid = int(memberid)
        st.sidebar.button(label='Submit')
    except ValueError:
        st.write('Enter a valid integer for Member No')
        return
    
        
    # policy_start_date = active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'Policy Inception'].values[0]
    # policy_end_date = active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'Policy Expiry'].values[0]
    policy_start_date = pd.to_datetime(active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'Policy Inception'].values[0])
    policy_end_date = pd.to_datetime(active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'Policy Expiry'].values[0])

    try:
        member_pa_value = utilization_data.loc[
            (utilization_data['MemberNo'] == memberid) &
            (utilization_data['EncounterDate'] >= policy_start_date) &
            (utilization_data['EncounterDate'] <= policy_end_date),
            'ApprovedPAAmount'].sum()
        member_pa_value = '#' + locale.format_string('%d', member_pa_value, grouping=True)
        membername = active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'Name'].values[0]
        client = active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'ClientName'].values[0]
        plan = active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'PlanType'].values[0]
        membertype = active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'MemberType'].values[0]
        memberage = active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'MemberAge'].values[0]
        member_utilization = utilization_data.loc[
            (utilization_data['EncounterDate'] >= policy_start_date) &
            (utilization_data['EncounterDate'] <= policy_end_date) &
            (utilization_data['MemberNo'] == memberid),
            ['Hospital', 'EncounterDate', 'Benefits', 'Speciality', 'ServiceDescription', 'ApprovedPAAmount' ]
        ].reset_index(drop=True)
    except IndexError:
        st.write('No data found for the given member number')
        return

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
        utilization_summary = member_utilization.groupby('Benefits')['ApprovedPAAmount'].sum().__round__(2)
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
    
display_member_utilization()







    




    











