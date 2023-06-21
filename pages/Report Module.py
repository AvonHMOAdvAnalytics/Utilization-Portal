import streamlit as st
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta
from PIL import Image
import altair as alt
from datetime import datetime, timedelta

image = Image.open('utilization_image.png')
st.image(image)

st.title('Utilization Report')
utilization_data = st.session_state['utilization_data']
active_enrollees = st.session_state['active_enrollees']


def aggregate_by_column(dataframe, date_column, groupby_column, sum_column,count_column, start_date, end_date):
    # Filter the dataframe by the selected date range
    filtered_df = dataframe[(dataframe[date_column] >= start_date) & (dataframe[date_column] <= end_date)]
    
    # Group the filtered dataframe by the groupby column and sum the values of the value column
    grouped_df = filtered_df.groupby(groupby_column).agg({sum_column: 'sum', count_column: 'nunique', 'MemberNo': 'nunique'}).reset_index()
    #[value_column].sum().reset_index(name='Sum of ' + value_column)

    #Sort the grouped dataframe by the sum column in descending order
    sorted_df = grouped_df.sort_values(sum_column, ascending=False).reset_index(drop=True)

    sorted_df = sorted_df.rename(columns={'ApprovedPAAmount':'Total PA Amount', 'AvonPaCode':'PA Generated', 'MemberNo':'No. of Enrollees'})
    
    # Display the result in a table in Streamlit
    st.write(sorted_df.head(20))



def top_10_chart(dataframe, date_column, category, value_column, start_date, end_date):
    # Filter the dataframe by the selected date range
    filtered_df = dataframe[(dataframe[date_column] >= start_date) & (dataframe[date_column] <= end_date)]
    
    # Group the filtered dataframe by the value column and sum the values
    grouped_df = filtered_df.groupby(category)[value_column].sum().reset_index(name=value_column)
    
    # Sort the grouped dataframe by the sum column in descending order
    sorted_df = grouped_df.astype({value_column: 'float'}).sort_values(value_column, ascending=False)
    
    # Select the top 10 rows from the sorted dataframe
    top_10_df = sorted_df.head(10)
    
    # Create a column chart using Altair
    chart = alt.Chart(top_10_df).mark_bar(color='#488948').encode(
        x=alt.X(value_column + ':Q',  axis=alt.Axis(title=value_column)),
        y=alt.Y(category + ':N',sort='-x', axis=alt.Axis(title=category)),
        tooltip = [alt.Tooltip(category, title=category), alt.Tooltip(value_column, title=value_column)]
    ).properties(
        width=600,
        height=500,
        title=f'Top 10 {category}s by {value_column} ({start_date} - {end_date})'
    )

    # Add the value labels to the bars
    value_labels = chart.mark_text(
        align='center',
        baseline='middle',
        dx=2,
        color='white'
    ).encode(
        text= value_column + ':Q'
    )
    
    # Display the chart in Streamlit
    st.altair_chart(chart)

def display_last_4_weeks_utilization(df, category_col):
    # Convert the Encounter date column to a datetime object
    df['EncounterDate'] = pd.to_datetime(df['EncounterDate'])
    
    # Determine the start and end dates of the last 4 weeks
    end_date = df['EncounterDate'].max()
    start_date = end_date - timedelta(weeks=4)
    
    # Filter the data to only include the last 4 weeks
    df = df.loc[(df['EncounterDate'] >= start_date) & (df['EncounterDate'] <= end_date)]
    
    # Group the data by week and appropriate category and sum the PA Value
    df = df.groupby([pd.Grouper(key='EncounterDate', freq='W-MON'), category_col])['ApprovedPAAmount'].sum().reset_index()
    
    #Pivot the data to display weeks as columns and products as rows
    df = df.pivot(index=category_col, columns='EncounterDate', values='ApprovedPAAmount')
    
    # Rename the columns to display the week start date
    df.columns = df.columns.strftime('%Y-%m-%d')

    # sort the data by the last column(the most recent week)
    df = df.sort_values(by=df.columns[-1], ascending=False)    

    st.subheader('Utilization over the past 4 Weeks by ' + category_col)
    st.dataframe(df.iloc[:, 1:])
   

def display_week_on_week_trend(df, column_name):
    # Convert the sales date column to a datetime object
    df['EncounterDate'] = pd.to_datetime(df['EncounterDate'])
    
    # Determine the start and end dates of the last 4 weeks
    end_date = df['EncounterDate'].max()
    start_date = end_date - timedelta(weeks=4)
    
    # Filter the data to only include the last 4 weeks
    df = df.loc[(df['EncounterDate'] >= start_date) & (df['EncounterDate'] <= end_date)]
    
    # Group the data by week and the specified column and calculate the sales total
    df = df.groupby([pd.Grouper(key='EncounterDate', freq='W-MON'), column_name])['ApprovedPAAmount'].sum().reset_index()
    
    # Pivot the data to display weeks as columns and the specified column as rows
    df = df.pivot(index=column_name, columns='EncounterDate', values='ApprovedPAAmount')
    
    
    # Rename the columns to display the week start date
    df.columns = df.columns.strftime('%Y-%m-%d')
    
    # Sort the data by the last column (the most recent week)
    df = df.sort_values(by=df.columns[-1], ascending=False)
    
    # Get the top 10 categories
    top_10_categories = df.head(10)
    
    
    # Transpose the data to display weeks as columns and the specified column as rows
    df = top_10_categories.T.reset_index().rename(columns={'EncounterDate': 'Week'})[1:]
    
    # Melt the data to convert columns into a "variable" column and a "value" column
    df = pd.melt(df, id_vars=['Week'], var_name=column_name, value_name='Total Weekly PA Value')
    
    # Create an Altair chart to display the week-on-week trend chart
    chart = alt.Chart(df).mark_line().encode(
        x='Week',
        y='Total Weekly PA Value',
        color=column_name,
        tooltip=[column_name, 'Week', 'Total Weekly PA Value']
    ).properties(
        width=800,
        height=500,
        title='Week-on-Week Utilization for ' + column_name.capitalize()
    )
    
    # Display the chart in Streamlit
    st.altair_chart(chart)


def display_sales_comparison_chart(df, column_name):
  # Convert the Encounter date column to a datetime object
    df['EncounterDate'] = pd.to_datetime(df['EncounterDate'])
    
    # Determine the start and end dates of the last 4 weeks
    end_date = df['EncounterDate'].max()
    start_date = end_date - timedelta(weeks=2)
    
    # Filter the data to only include the last 4 weeks
    previous_df = df.loc[(df['EncounterDate'] >= start_date) & (df['EncounterDate'] <= end_date)]
    
    # Group the data by week and appropriate category and sum the PA Value
    previous_df = previous_df.groupby([pd.Grouper(key='EncounterDate', freq='W-MON'), column_name])['ApprovedPAAmount'].sum().reset_index()
    
    #Pivot the data to display weeks as columns and products as rows
    previous_df = previous_df.pivot(index=column_name, columns='EncounterDate', values='ApprovedPAAmount')

    previous_month = pd.to_datetime('today').to_period('M') - 1

    previous_month_df = df[df['EncounterDate'].dt.to_period('M') == previous_month]

    previous_month_average = (previous_month_df.groupby(column_name)['ApprovedPAAmount'].sum()/4).reset_index()

    compare_df = previous_df.merge(previous_month_average[[column_name,'ApprovedPAAmount']], on = column_name)#.set_index(column_name)

    compare_df = compare_df.iloc[:,[0,2,3,4]]

    old_columns = compare_df.iloc[:,[1,2,3]].columns.tolist()
    new_columns = ['Previous Week', 'Current Week', 'Previous Month Weekly Average']

    for old_col, new_col in zip(old_columns, new_columns):
        compare_df = compare_df.rename(columns={old_col: new_col})

    compare_df = compare_df.sort_values(by=compare_df.columns[-2], ascending=False)
    compare_df = compare_df.head(10)
    chart_data = pd.melt(compare_df.head(10), id_vars = column_name, value_vars=['Previous Week', 'Current Week', 'Previous Month Weekly Average'],
                          var_name='Period', value_name='Value')
    
    
    #Create the Altair chart
    chart = alt.Chart(chart_data).mark_bar().encode(
        # column = alt.Column(column_name,spacing=0,header=alt.Header(labelOrient='bottom')),
        x = alt.X(column_name, axis=alt.Axis(ticks=False)),
        y=alt.Y('Value'),
        color=alt.Color('Period'),
        # column=alt.Column('Period', title='Period', sort=['Previous Week', 'Current Week', 'Previous Month Weekly Average']),
        tooltip=[column_name,'Period','Value'],
    ).properties(
        width=800,
        height=500
    )
    
    
    # Display the chart using Streamlit
    st.altair_chart(chart, use_container_width=True)


def display_monthly_utilization(df):
    # Convert the Encounter date column to a datetime object
    df['EncounterDate'] = pd.to_datetime(df['EncounterDate'])
    
    # Determine the start and end dates of the past 6 months
    end_date = df['EncounterDate'].max()
    start_date = end_date - pd.DateOffset(months=6) + pd.DateOffset(days=1)  # Add 1 day to start from the next month
    
    # Filter the data to only include the past 6 months
    df = df.loc[(df['EncounterDate'] >= start_date) & (df['EncounterDate'] <= end_date)]
    
    # Group the data by month and calculate the total utilization
    df = df.groupby(pd.Grouper(key='EncounterDate', freq='M'))['ApprovedPAAmount'].sum().reset_index()
    
    # Generate a list of month-year labels for the table columns
    month_labels = [datetime.strftime(m, '%b-%Y') for m in pd.date_range(start_date, end_date, freq='M')]
    
    # Create an empty DataFrame to store the monthly utilization
    result = pd.DataFrame(columns=['Month', 'Total Utilization'])
    
    # Iterate through the month-year labels and add the corresponding utilization to the DataFrame
    for month_label in month_labels:
        month = datetime.strptime(month_label, '%b-%Y')
        utilization_df = df.loc[df['EncounterDate'] == month, 'ApprovedPAAmount']
        if not utilization_df.empty:
            utilization = utilization_df.values[0]
            result = result.append({'Month': month_label, 'Total Utilization': utilization}, ignore_index=True)
        else:
            result = result.append({'Month': month_label, 'Total Utilization':0}, ignore_index=True)
    
    return result


options = st.sidebar.radio('Report Mode', options=['Overall Report', 'Weekly Report'])

wellness = ['ANNUAL HEALTH CHECK ADVANCED', 'ANNUAL HEALTH CHECK BASIC', 'ANNUAL HEALTH CHECK COMPREHENSIVE', 'ANNUAL HEALTH CHECK PRINCIPAL ONLY']
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

if options == 'Overall Report':
    start_date = pd.to_datetime(st.sidebar.date_input('Start Date',min_value=dt.datetime.now().date()-relativedelta(years=1)))
    end_date = pd.to_datetime(st.sidebar.date_input('End Date',max_value=dt.datetime.now().date()))
    benefit = st.selectbox(label='Select Benefit', options=('All','Consultation','Drugs','Chronic Disease','Optical', 'Dental', 'Lab Investigation', 'Wellness', 'Surgery', 'Maternity', 'Others'))

    
    df = utilization_data.loc[
            (utilization_data['EncounterDate'] >= start_date) &
            (utilization_data['EncounterDate'] <= end_date) &
            (utilization_data['New Approval Status'] == 'APPROVED'),
            ['AvonPaCode','Client','EnrolleeName','Sex','Relation', 'MemberNo','PlanName','ProviderName', 'State', 'CaseManager', 'EncounterDate', 'Benefit','Diagnosis', 'Speciality', 'ServiceDescription', 'ApprovedPAAmount' ]
            ]
    
    if benefit == 'All':
        data = df
    elif benefit == 'Consultation':
        data = df.loc[df['Benefit'].isin(consultation)]
    elif benefit == 'Drugs':
        data = df.loc[df['Benefit'].isin(drugs)]
    elif benefit == 'Chronic Disease':
        data = df.loc[df['Benefit'] == 'CHRONIC DISEASE MANAGEMENT']
    elif benefit == 'Optical':
        data = df.loc[df['Benefit'].isin(optical)]
    elif benefit == 'Dental':
        data = df.loc[df['Benefit'].isin(dental)]
    elif benefit == 'Surgery':
        data = df.loc[df['Benefit'].isin(surgery)]
    elif benefit == 'Lab Investigation':
        data = df.loc[df['Benefit'].isin(lab_investigation)]
    elif benefit == 'Wellness':
        data = df.loc[df['Benefit'].isin(wellness)]
    elif benefit == 'Maternity':
        data = df.loc[df['Benefit'].isin(maternity)]
    else:
        data = df[~df['Benefit'].isin(others)]

    pa_value = int(data['ApprovedPAAmount'].sum())
    pa_value = '#' + '{:,}'.format(pa_value) 
    pa_count = data['AvonPaCode'].nunique()
    pa_count = '{:,}'.format(pa_count) 
    member_count = data['MemberNo'].nunique()
    member_count = '{:,}'.format(member_count) 
    
    st.subheader('Total utilization between ' + str(start_date.date()) + ' and ' + str(end_date.date()))
    col1, col2 = st.columns(2)
    col1.metric(label = 'Total PA Value', value = pa_value)
    col2.metric(label = 'Total PA Count', value = pa_count)

    st.metric(label='Total Enrollees Who Accessed Care', value=member_count)

    st.subheader('List of Top 20 Hospitals by Approved PA Amount')
    aggregate_by_column(data, 'EncounterDate', 'ProviderName', 'ApprovedPAAmount','AvonPaCode', start_date, end_date)

    top_10_chart(data, 'EncounterDate','ProviderName', 'ApprovedPAAmount', start_date, end_date)

    st.subheader('List of Top 20 Clients by Approved PA Amount')
    aggregate_by_column(data, 'EncounterDate', 'Client', 'ApprovedPAAmount','AvonPaCode', start_date, end_date)
    top_10_chart(data, 'EncounterDate','Client', 'ApprovedPAAmount', start_date, end_date)

    st.subheader('List of Top 20 Benefits by Approved PA Amount')
    aggregate_by_column(data, 'EncounterDate', 'Benefit', 'ApprovedPAAmount','AvonPaCode', start_date, end_date)
    top_10_chart(data, 'EncounterDate','Benefit', 'ApprovedPAAmount', start_date, end_date)

    st.subheader(benefit + ' Utilization Data between ' + str(start_date.date()) + ' and ' + str(end_date.date()))
    st.dataframe(data)

    st.download_button(
            label='Download data as Excel File',
            data=data.to_csv().encode('utf-8'),
            file_name=str(benefit + ' utilization between ' + str(start_date.date()) + ' and ' + str(end_date.date()) + '.csv'),
            mime='text/csv',
            )
elif options == 'Weekly Report':
    display_last_4_weeks_utilization(utilization_data, 'ProviderName')
    display_week_on_week_trend(utilization_data,'ProviderName')
    display_sales_comparison_chart(utilization_data, 'ProviderName')

    display_last_4_weeks_utilization(utilization_data, 'Client')
    display_week_on_week_trend(utilization_data, 'Client')
    display_sales_comparison_chart(utilization_data, 'Client')

    display_last_4_weeks_utilization(utilization_data, 'Benefit')
    display_week_on_week_trend(utilization_data, 'Benefit')
    display_sales_comparison_chart(utilization_data, 'Benefit')

    pending_df = utilization_data.loc[utilization_data['New Approval Status'].isnull()]


    pending_df['EncounterDate'] = pd.to_datetime(pending_df['EncounterDate'])

    pending_df.set_index('EncounterDate', inplace=True)

    aggregate_data = pending_df[pending_df['InitialApprovalStatus'] == 'PENDING'].groupby(pd.Grouper(freq='W-MON')).agg({
        'FinalPAAmount': 'sum',
        'AvonPaCode':'nunique' 
    })

    aggregate_data['Rejected_PA_Value'] = pending_df[pending_df['InitialApprovalStatus'] == 'REJECTED'].groupby(pd.Grouper(freq='W-MON')).agg({
        'FinalPAAmount': 'sum'
    })
    aggregate_data['Rejected_PA_Count'] = pending_df[pending_df['InitialApprovalStatus'] == 'REJECTED'].groupby(pd.Grouper(freq='W-MON')).agg({
        'AvonPaCode': 'nunique'
    })

    approved_df = utilization_data.loc[utilization_data['New Approval Status'] == 'APPROVED']
    approved_df['EncounterDate'] = pd.to_datetime(approved_df['EncounterDate'])
    approved_df.set_index('EncounterDate', inplace=True)
    aggregate_data['Approved_PA_Value'] = approved_df[approved_df['New Approval Status'] == 'APPROVED'].groupby(pd.Grouper(freq='W-MON')).agg({
        'ApprovedPAAmount':'sum'})
    aggregate_data['Approved_PA_Count'] = approved_df[approved_df['New Approval Status'] == 'APPROVED'].groupby(pd.Grouper(freq='W-MON')).agg({
        'AvonPaCode':'nunique'})
    
    aggregate_data = aggregate_data.rename(columns={'FinalPAAmount': 'Pending_PA_Value', 'AvonPaCode':'Pending_PA_Count'})
    aggregate_data = aggregate_data.tail(3)
    # aggregate_data.index = aggregate_data.index.astype(str)

    #aggregate_data = aggregate_data.rename(index={0: 'Previous Week', 1: 'Current Week'}, inplace=True)


    st.write(aggregate_data)
