import streamlit as st
import pandas as pd
import pyodbc
import datetime as dt
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import bcrypt
import os
 
st.set_page_config(page_title='PA Utilization Portal', layout='wide', initial_sidebar_state='expanded')

# def load_config():
#     with open('config.yaml') as file:
#         config = yaml.load(file, Loader=SafeLoader)
#     for user in config['credentials']['usernames']:
#         password_env_var = config['credentials']['usernames'][user]['password'].strip('${}')
#         config['credentials']['usernames'][user]['password'] = os.getenv(password_env_var)
#     config['cookie']['key'] = os.getenv(config['cookie']['key'].strip('${}'))
#     return config

# config = load_config()
 
# Load configuration from YAML file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Hash passwords if not already hashed
for user in config['credentials']['usernames']:
    plain_password = config['credentials']['usernames'][user]['password']
    if not plain_password.startswith('$2b$'):
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        config['credentials']['usernames'][user]['password'] = hashed_password.decode('utf-8')
 
# Instantiate the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config.get('preauthorized', [])
)
 
# Database connection
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

def main():
    # Initialize session state variables if they don't exist
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if st.session_state['authentication_status']:
        st.title("Home Page")
        st.write(f"You are logged in as {st.session_state['name']} ({st.session_state['username']})")

        #sidebar navigation
        st.sidebar.title("Navigation")
        if st.session_state['username'].startswith("admin"):
            choice = st.sidebar.radio("Select Module", ["Enrollee Module", "Client Module","Provider Module", 'Report Module'])
        elif st.session_state['username'].startswith("contact"):
            choice = st.sidebar.radio("Select Module", ["Enrollee Module"])
        elif st.session_state['username'].startswith("medical"):
            choice = st.sidebar.radio("Select Module", ["Provider Module"])
        elif st.session_state['username'].startswith("audit"):
            choice = st.sidebar.radio("Select Module", ["Client Module", "Provider Module", "Report Module"])
        else:
            st.error('Access Denied: Invalid Role.')
            return

        # Dynamically load the module based on the username
        try:
            # Define a function to execute a module in a separate namespace
            def execute_module(module_name):
                with open(module_name) as file:
                    module_code = file.read()
                module_namespace = {'conn': conn, 'conn1':conn1, 'st': st, 'pd': pd, 'dt': dt}
                exec(module_code, module_namespace)

            if choice == "Enrollee Module":
                execute_module("EnrolleeModule.py")
            elif choice == "Client Module":
                execute_module("Client Module.py")
            elif choice == "Provider Module":
                execute_module("Provider Module.py")
            elif choice == "Report Module":
                execute_module("Report Module.py")
            
        except FileNotFoundError as e:
            st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

        # Add the logout button in the sidebar
        with st.sidebar:
            if authenticator.logout('Logout', 'main'):
                st.session_state['name'] = None
                st.session_state['authentication_status'] = None
                st.session_state['username'] = None
                st.experimental_rerun()
    else:
        # Display the login page
        st.title("Home Page")
        st.write("Login with your username and password to access the portal.")
        name, authentication_status, username = authenticator.login('Login', 'main')

        if authentication_status:
            st.session_state['name'] = name
            st.session_state['authentication_status'] = authentication_status
            st.session_state['username'] = username
            st.experimental_rerun()
        elif authentication_status is False:
            st.error("Username/password is incorrect")
        elif authentication_status is None:
            st.warning("Please enter your username and password")

if __name__ == "__main__":
    main()