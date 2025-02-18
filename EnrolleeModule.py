import streamlit as st
import pandas as pd
import pyodbc
from PIL import Image
import datetime as dt
import os

# st.set_page_config(page_title= 'Enrollee Utilization',layout='wide', initial_sidebar_state='expanded')


#locale.setlocale(locale.LC_ALL, 'en_US')
image = Image.open('EnrolleModule.png')
st.image(image, use_column_width=True)


options = st.sidebar.radio('Module', options=['Enrollee Bio-Data', 'Enrollee Utilization Summary', 'Enrollee Benefit Limit'])

query = 'SELECT PolicyNo\
            ,ClientName\
            ,Supposed_Policy_Inception as [Policy Inception]\
            ,Supposed_Policy_Expiry as [Policy Expiry]\
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
             from [dbo].[tbl_ModifiedMemberMasterView]'

query1 = 'SELECT distinct * from utilization_portal_data'
query2 = 'select distinct LoginMemberNo, DateCreated,  LastLoginDate, IsActive\
            from Users \
            where LastLoginDate is not null'
query3 = 'select PolicyNo, PlanType, CancerCareLimit, GlassesLimit, MaternityLimit,OpticalCareLimit, DentalCareLimit,\
            SurgeryLimit, TotalLimit, FromDate, ToDate\
            from tblBenefitLimit'

# define the connection for the DBs when working on the local environment
# conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
#         +st.secrets['server']
#         +';DATABASE='
#         +st.secrets['database']
#         +';UID='
#         +st.secrets['username']
#         +';PWD='
#         +st.secrets['password']
#         ) 

# conn1 = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
#         +st.secrets['server1']
#         +';DATABASE='
#         +st.secrets['database1']
#         +';UID='
#         +st.secrets['username1']
#         +';PWD='
#         +st.secrets['password1']
#         ) 

#define the connections for the DBs when deployed to cloud
#assign credentials for the avondw DB credentials
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
#assign credentials for the avon flex DB credentials
server1 = os.environ.get('server_name1')
database1 = os.environ.get('db_name1')
username1 = os.environ.get('db_username1')
password1 = os.environ.get('password1')
conn1 = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
        + server1
        +';DATABASE='
        + database1
        +';UID='
        + username1
        +';PWD='
        + password1
        )

@st.cache_data(ttl = dt.timedelta(hours=24))
def get_data_from_sql():
    active_enrolees = pd.read_sql(query, conn)
    utilization_data = pd.read_sql(query1, conn)
    app_data = pd.read_sql(query2, conn1)
    limit_df = pd.read_sql(query3, conn)
    conn.close()
    return active_enrolees, utilization_data, app_data, limit_df

active_enrollees, utilization_data, app_data, limit_df  = get_data_from_sql()

utilization_data['PAIssueDate'] = pd.to_datetime(utilization_data['PAIssueDate']).dt.date

utilization_data['MemberNo'] = utilization_data['MemberNo'].astype(str)

active_enrollees['MemberNo'] = active_enrollees['MemberNo'].astype(str)

# active_enrollees, utilization_data = get_data_from_sql()

# limit_df = pd.read_csv('Benefit_Limits.csv')

st.session_state['utilization_data'] = utilization_data
st.session_state['active_enrollees'] = active_enrollees

memberid = st.sidebar.text_input('Enrollee Member ID')
st.sidebar.button(label='Submit')

 # Helper function to format limits and utilization values
def format_value(value):
    if pd.notna(value):  # Check for non-NaN values
        return '#' + '{:,}'.format(int(value))
    return None

# Helper function to calculate utilization and filter relevant rows
def filter_utilization(member_utilization, benefit_keywords, service_keywords):
    return member_utilization.loc[
        member_utilization['Benefit'].str.contains('|'.join(benefit_keywords), case=False, na=False) |
        member_utilization['ServiceDescription'].str.contains('|'.join(service_keywords), case=False, na=False)
    ]

def display_member_utilization(mem_id):   
    if not mem_id.isdigit():
        st.write('Enter a valid MemberNo')
        return 
    policyno = active_enrollees.loc[active_enrollees['MemberNo'] == memberid, 'PolicyNo'].iat[0]
    # mem_id = int(mem_id)

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
    member_pa_value = '#' + '{:,}'.format(int(member_pa_value))       
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
            ['AvonPaCode','ProviderName', 'EncounterDate','PAIssueDate', 'Benefit', 'Diagnosis', 'Speciality', 'ServiceDescription','State', 'ProviderManager', 'ApprovedPAAmount' ]
        ].set_index('AvonPaCode')
    
    #ensure the memberno column is converted to integer
    app_data['LoginMemberNo'] = app_data['LoginMemberNo'].astype(int)
    #assign the last_login_date to a variable for the requested memberid
    if mem_id in app_data['LoginMemberNo'].values:
        last_login_date = app_data.loc[app_data['LoginMemberNo'] == mem_id, 'LastLoginDate'].iat[0]
    else:
        last_login_date = None
    #create 2 new columns in active enrollees where the id is also present in the app_data
    active_enrollees['AppLogin?'] = active_enrollees['MemberNo'].isin(app_data['LoginMemberNo']).map({True: 'Active', False: 'Not Active'})
    active_enrollees['Last_Login_Date'] = active_enrollees['MemberNo'].isin(app_data['LoginMemberNo']).map({True: last_login_date, False: 'None'})
    #assign the app status and last login date to a varaible as shown below
    enrollee_app_status = active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'AppLogin?'].iat[0]
    last_login_date = active_enrollees.loc[active_enrollees['MemberNo'] == mem_id, 'Last_Login_Date'].iat[0]

    
    if membername is not None and options == 'Enrollee Bio-Data':  
        #col1,col2= st.columns(2)
        st.metric(label = 'Enrollee Name', value = membername)
        st.metric(label = 'Enrollee Client', value = client)
        st.metric(label = 'Enrollee Plan', value = plan)
        st.metric(label = 'Total Utilization Within Current Policy', value=member_pa_value)

        col3, col4 = st.columns(2)
        col3.metric(label = 'Enrollee Age', value = memberage)
        col4.metric(label = 'Member Type', value = membertype)

        col5, col6 = st.columns(2)        
        col5.metric(label = 'Policy Inception', value = str(policy_start_date.date()))
        col6.metric(label = 'PolicyExpiry', value = str(policy_end_date.date()))

        col7, col8 = st.columns(2)
        col7.metric(label = 'Downloaded AVON Flex App?', value=enrollee_app_status)
        col8.metric(label='Last Login Date', value=str(last_login_date))
        
        # except IndexError:
        #     st.write("Enrollee not available")
    elif len(member_utilization) > 0 and options == 'Enrollee Utilization Summary':
        st.subheader('Utilization summary for ' + membername)
        utilization_summary = member_utilization.groupby('Benefit')['ApprovedPAAmount'].sum().__round__(2)
        st.dataframe(utilization_summary, use_container_width=True)
        st.subheader('Utilization details for '+ membername)
        st.dataframe(member_utilization,use_container_width=True)
    elif options == 'Enrollee Benefit Limit':
        enrollee_benefit_limit = limit_df.loc[
                (limit_df['PolicyNo'] == policyno) &
                (limit_df['PlanType'] == plan)
            ]

        # Extract and format benefit limits
        limits = {
            "Cancer Care": format_value(enrollee_benefit_limit['CancerCareLimit'].iat[0]),
            "Glasses": format_value(enrollee_benefit_limit['GlassesLimit'].iat[0]),
            "Maternity": format_value(enrollee_benefit_limit['MaternityLimit'].iat[0]),
            "Optical Care": format_value(enrollee_benefit_limit['OpticalCareLimit'].iat[0]),
            "Dental Care": format_value(enrollee_benefit_limit['DentalCareLimit'].iat[0]),
            "Surgery": format_value(enrollee_benefit_limit['SurgeryLimit'].iat[0]),
            "Total Limit": format_value(enrollee_benefit_limit['TotalLimit'].iat[0])
        }

        # Define keywords for each benefit category
        benefit_keywords = {
            "Cancer Care": ["Cancer"],
            "Glasses": ["Glasses"],
            "Maternity": ["Maternity"],
            "Optical Care": ["Optic"],
            "Dental Care": ["Dental"],
            "Surgery": ["Surger"]
        }

        service_keywords = {
            "Cancer Care": ["Cancer"],
            "Glasses": ["Glasses"],
            "Maternity": ["Antenatal"],
            "Optical Care": ["Optical"],
            "Dental Care": ["Scaling"],
            "Surgery": ["Caesarian", "Appendectomy", "Hysterectomy", "Mastectomy", "C/S", "Laparotomy", "Hemorrhoidectomy", "Herniorrhaphy", "Thyroidectomy", "Cholecystectomy", "Laparoscopy"]
        }

        #prepare and display metrics with granular details
        used_rows = pd.DataFrame()

        # Prepare and display metrics with granular details
        for benefit, keywords in benefit_keywords.items():
            # Filter and calculate utilization
            benefit_data = filter_utilization(member_utilization, keywords, service_keywords[benefit])
            benefit_utilization = benefit_data['ApprovedPAAmount'].sum()
            utilization_formatted = format_value(benefit_utilization)
            limit = limits[benefit]

            if limit is not None:
                st.metric(label=benefit, value=f"{utilization_formatted}/{limit}")

                # Add granular details in an expander
                with st.expander(f"View Utilization Details for {benefit}"):
                    if not benefit_data.empty:
                        st.dataframe(benefit_data[['PAIssueDate', 'ServiceDescription', 'ApprovedPAAmount']])
                        #Add benefit data to used rows to avoid duplication
                        used_rows = pd.concat([used_rows, benefit_data])
                    else:
                        st.write("No utilization details available for this benefit.")

        #Calculate the remaining utilization rows not categorised under any benefit
        remaining_data = member_utilization.loc[~member_utilization.index.isin(used_rows.index)]
        remaining_utilization = remaining_data['ApprovedPAAmount'].sum()
        remaining_formatted = format_value(remaining_utilization)

        # Display total limit
        if limits["Total Limit"] is not None:
            st.metric(label="Total Limit", value=f"{member_pa_value}/{limits['Total Limit']}")
            #add granular details for the remaining utilization
            with st.expander('View details for all other Utilization'):
                if not remaining_data.empty:
                    st.dataframe(remaining_data[['PAIssueDate', 'ServiceDescription', 'ApprovedPAAmount']])
                else:
                    st.write("No additional utilization details available.")


        # st.write(enrollee_benefit_limit)
        # null_cols = enrollee_benefit_limit.columns[enrollee_benefit_limit.isnull().all()]
        # enrollee_benefit_limit.drop(null_cols, axis = 1, inplace = True)
        # # enrollee_benefit_limit = enrollee_benefit_limit.iloc[:, 6:].reset_index(drop=True)
        # enrollee_benefit_limit = enrollee_benefit_limit.to_dict('index')
        
        # st.write(enrollee_benefit_limit)
        return

display_member_utilization(memberid)
