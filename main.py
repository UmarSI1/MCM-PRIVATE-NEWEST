
import pickle
import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import io
import concurrent.futures
import re
import altair as alt


from general import *
from general_temp_for_company import *
from general_temp_for_harm import *
from general_temp_for_harm_and_comp import *



#################################
#defining unchanging globals
list_of_companies = ['TikTok', 'Pinterest', 'Snapchat', 'LinkedIn', 'X', 'Facebook', 'Instagram','YouTube','Reddit','Bumble','Threads','WhatsApp Channels','Pornhub','Stripchat','Tinder','Discord Netherlands B.V.','Campfire','Badoo','Hinge','Badoo']
#'Uber' not in list

list_of_harms = ['STATEMENT_CATEGORY_ILLEGAL_OR_HARMFUL_SPEECH', 'STATEMENT_CATEGORY_SCOPE_OF_PLATFORM_SERVICE', 'STATEMENT_CATEGORY_PROTECTION_OF_MINORS', 'STATEMENT_CATEGORY_VIOLENCE', 'STATEMENT_CATEGORY_PORNOGRAPHY_OR_SEXUALIZED_CONTENT', 
                        'STATEMENT_CATEGORY_DATA_PROTECTION_AND_PRIVACY_VIOLATIONS', 'STATEMENT_CATEGORY_SCAMS_AND_FRAUD', 'STATEMENT_CATEGORY_SELF_HARM', 
                        'STATEMENT_CATEGORY_NEGATIVE_EFFECTS_ON_CIVIC_DISCOURSE_OR_ELECTIONS', 'STATEMENT_CATEGORY_INTELLECTUAL_PROPERTY_INFRINGEMENTS', 
                        'STATEMENT_CATEGORY_UNSAFE_AND_ILLEGAL_PRODUCTS', 'STATEMENT_CATEGORY_NON_CONSENSUAL_BEHAVIOUR', 'STATEMENT_CATEGORY_ANIMAL_WELFARE', 
                        'STATEMENT_CATEGORY_RISK_FOR_PUBLIC_SECURITY']


category_descriptions = {
        'STATEMENT_CATEGORY_SCOPE_OF_PLATFORM_SERVICE': 'PLATFORM SCOPE',
        'STATEMENT_CATEGORY_DATA_PROTECTION_AND_PRIVACY_VIOLATIONS': 'GDPR VIOLATION',
        'STATEMENT_CATEGORY_PORNOGRAPHY_OR_SEXUALIZED_CONTENT': 'PORN/SEX CONTENT',
        'STATEMENT_CATEGORY_ILLEGAL_OR_HARMFUL_SPEECH': 'ILLEGAL/HARMFULL SPEECH',
        'STATEMENT_CATEGORY_VIOLENCE': 'VIOLENCE',
        'STATEMENT_CATEGORY_SCAMS_AND_FRAUD': 'SCAMS/FRAUD',
        'STATEMENT_CATEGORY_UNSAFE_AND_ILLEGAL_PRODUCTS': 'ILLEGAL PRODUCTS',
        'STATEMENT_CATEGORY_NON_CONSENSUAL_BEHAVIOUR': 'NON CONSENSUAL BEHAVIOUR',
        'STATEMENT_CATEGORY_PROTECTION_OF_MINORS': 'PROTECT MINORS',
        'STATEMENT_CATEGORY_INTELLECTUAL_PROPERTY_INFRINGEMENTS': 'COPYRIGHT',
        'STATEMENT_CATEGORY_NEGATIVE_EFFECTS_ON_CIVIC_DISCOURSE_OR_ELECTIONS': 'NEGATIVE EFFECTS ELECTIONS',
        'STATEMENT_CATEGORY_RISK_FOR_PUBLIC_SECURITY': 'RISK PUBLIC SECURITY',
        'STATEMENT_CATEGORY_ANIMAL_WELFARE': 'ANIMAL WELFARE',
        'STATEMENT_CATEGORY_SELF_HARM': 'SELF HARM'
    }

#################################



##############################################################################################################  --- Connecting to azure / getting datasets --- ###############################################################################################################

# # Azure Blob Storage configuration
connection_string = 'DefaultEndpointsProtocol=https;AccountName=asatrustandsafetycv;AccountKey=HrJteCB33VFGftZQQFcp0AL1oiv6XOYtUD7FHosKK67v6+KLTmYLrQSrEL0Np+ODbZrCUNvvZ2Zd+AStGD1jPw==;EndpointSuffix=core.windows.net'
container_name = 'dsanew'

# connecting to azure and getting all blobs in container
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)
blobs_list = container_client.list_blobs()

#assigning each blob in list to a dataset
unorganised_datasets = [blob.name for blob in blobs_list]
#datasets = [filename for filename in unorganised_datasets if re.match(r'^\d', filename)]

datasets = [
    filename for filename in unorganised_datasets
    if re.match(r'^\d', filename) and 'historical' not in filename.lower()
]

#reversing datasets to get latest dataset first
for i in range(len(datasets)):
    if datasets[i].endswith(".pkl"):
        datasets[i] = datasets[i][:-4]
datasets.reverse()

##################################################################################################################################################################################################################################################################################



########################################
#Fetches the seelected dataset from the blob list and donwloads it and filters needed data e.G. (list_of_companies)
def load_data_from_dataset(selected_dataset):
    blob_name = selected_dataset
    blob_client = container_client.get_blob_client(blob_name)
    
    # Download the blob content to bytes
    download_stream = blob_client.download_blob()
    blob_data = download_stream.readall()

    # Convert bytes to a file-like object
    data = pickle.load(io.BytesIO(blob_data))

    # Extract necessary lists
    List_of_companies = list(data.keys())
    harm_dic = data[List_of_companies[0]]
    List_of_harms = list(harm_dic.keys())
    content_dic = harm_dic[List_of_harms[0]]
    List_of_content_type = list(content_dic.keys())
    action_dic = content_dic[List_of_content_type[0]]
    List_of_moderation_action = list(action_dic.keys())
    automation_dic = action_dic[List_of_moderation_action[0]]
    List_of_automation_status = list(automation_dic.keys())

    #(List_of_companies)
    
    #Returning the necessary lists
    return data, List_of_companies, List_of_harms, List_of_content_type, List_of_moderation_action, List_of_automation_status
########################################



########################################
def load_data(selected_dataset):
    """Load data from the blob storage."""
    blob_name = f"{selected_dataset}.pkl"
    #print(blob_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    # Download the blob content to bytes and load it as a dictionary
    download_stream = blob_client.download_blob()
    blob_data = download_stream.readall()
    
    return pickle.load(io.BytesIO(blob_data))
########################################



def plot_acc_totals_per_harm_company_harm_historical_orig(data, company_selected, harm_selected):
    """ Sum all numbers for acc per harm and return the results. """
    
    # acc_totals_per_harm =  data[company_selected][harm_selected]['Yes']
    # manual_totals_per_harm = data[company_selected][harm_selected]['No']
    
    if company_selected not in data:
        acc_totals_per_harm =  0
        manual_totals_per_harm = 0
    else:
        if harm_selected not in data[company_selected]:
            acc_totals_per_harm =  0
            manual_totals_per_harm = 0
        else:
            acc_totals_per_harm =  data[company_selected][harm_selected]['Yes']
            manual_totals_per_harm = data[company_selected][harm_selected]['No']
            
    
    return acc_totals_per_harm, manual_totals_per_harm

    
########################################
# 


##############################################################################################################  --- Streamlit Page --- #####################################################################################################################

def main():

    st.set_page_config(layout="wide")
    st.write('<h1 style="text-align: center; text-decoration: underline;">Content moderation daily monitor</h1>', unsafe_allow_html=True)
    st.write('<h4 style="text-align: center;">This dashboard presents the daily count of moderation actions categorized by harm and platform provided by the DSA Transparency Database.</h4>', unsafe_allow_html=True)
    st.markdown("---")
    
    
##############################################################################################################  --- FYI Section --- #########################################################################################################################

    with st.expander("When using this dashboard, please consider the following points: ", expanded=True):
        st.markdown("""
            **Please take into consideration:**

            - The definitions of harms may differ from those used by Ofcom.
            - This data reflects the DSA transparency report data from the EU, which does not include the UK.
            - Use this data as an initial investigation into trends and insights that may be transferable to the UK.
            - Different services may use varying standards and methodologies for reporting data, leading to inconsistencies that can affect comparability.
            - Since the data is self-reported, there is often no independent verification to ensure its accuracy and completeness.
            - Services might present data in a way that portrays their content moderation efforts more favorably, potentially downplaying issues or overemphasizing successes.
            - Self-reported data might not be updated frequently, leading to potential discrepancies between reported data and current practices.
            - As noted, the data reflects the EU context and may not fully capture the nuances of content moderation practices in the UK.
        """)



##############################################################################################################  --- Historical Analysis --- ##################################################################################################################

    with st.expander("Harm definition's according to the DSA documentation", expanded=False):
    
        question = st.selectbox(
            "Select a Harm",
            ["Animal welfare", "Data protection and privacy violations", "Illegal or harmful speech", "Intellectual property infringements", "Negative effects on civic discourse or elections", 
             "Non-consensual behaviour", "Online bullying/intimidation", "Pornography or sexualized content", "Protection of minors", "Risk for public security", "Scams and/or fraud", "Self-harm", 
             "Scope of platform service", "Unsafe and/or illegal products", "Violence"])
        
        if question == "Animal welfare":
            st.write("This category includes: Animal harm, Unlawful sale of animals.")
        elif question == "Data protection and privacy violations":
            st.write("This category includes: Biometric data breach, Missing processing ground for data, Right to be forgotten, Data falsification.")
        elif question == "Illegal or harmful speech":
            st.write("This category includes: Defamation, Discrimination, Hate speech.")
        elif question == "Intellectual property infringements":
            st.write("This category includes: Copyright infringement, Design infringement, Geographical indications infringements, Patent infringement, Trade secret infringement, Trademark infringement.")
        elif question == "Negative effects on civic discourse or elections":
            st.write("This category includes: Disinformation, Foreign information manipulation and interference, Misinformation.")
        elif question == "Non-consensual behaviour":
            st.write("This category includes: Non-consensual image sharing, Non-consensual items containing deepfake or similar technology using a third party’s features.")
        elif question == "Online bullying/intimidation":
            st.write("This category includes: Stalking.")
        elif question == "Pornography or sexualized content":
            st.write("This category includes: Adult sexual material, Image-based sexual abuse (excluding content depicting minors).")
        elif question == "Protection of minors":
            st.write("This category includes: Age-specific restrictions concerning minors, Child sexual abuse material, Grooming/sexual enticement of minors, Unsafe challenges.")
        elif question == "Risk for public security":
            st.write("This category includes: Illegal organizations, Risk for environmental damage, Risk for public health, Terrorist content.")
        elif question == "Scams and/or fraud":
            st.write("This category includes: Inauthentic accounts, Inauthentic listings, Inauthentic user reviews, Impersonation or account hijacking, Phishing, Pyramid schemes.")
        elif question == "Self-harm":
            st.write("This category includes: Content promoting eating disorders, Self-mutilation, Suicide.")
        elif question == "Scope of platform service":
            st.write("This category includes: Age-specific restrictions, Geographical requirements, Goods/services not permitted to be offered on the platform, Language requirements, Nudity.")
        elif question == "Unsafe and/or illegal products":
            st.write("This category includes: Insufficient information on traders, Regulated goods and services, Dangerous toys.")
        elif question == "Violence":
            st.write("This category includes: Coordinated harm, Gender-based violence, Human exploitation, Human trafficking, Incitement to violence and/or hatred.")
    
    
    st.write('<h2 style="text-align: center; text-decoration: underline;">Historical Analysis</h2>', unsafe_allow_html=True)

    selected_option = st.radio(
        "In this historical analysis you can select one of the following options",
        options=["Evaluate a certain company or harm category", "Evaluate two companies for the same harm category", "Evaluate two harm categories for the company"],
        index=0
    )


    
    #sort this out do we need data?
    data = [datetime.strptime(d, "%Y-%m-%d") for d in datasets]

    #setting the initial date to a defult of 5 days ago and formatting it to YYYY-MM-DD
    today = datetime.now().date()
    initial_date = today - timedelta(days=4)
    initial_date_str = initial_date.strftime("%Y-%m-%d")




    second_company_selected = None
    second_harm_selected = None

    if selected_option == "Evaluate two companies for the same harm category":
        second_harm_selected = None
        #st.write("You selected 'Company'.")


        date_initial, date_final, company_intial,  second_company, harm_intial = st.columns(5)

        with date_initial:
            filtered_dates_for_initial_date_input = [date for date in datasets if date <= initial_date_str]
            st.markdown("<h4 style=' text-decoration: underline;'>Select an Inital Date:</h4>", unsafe_allow_html=True) 
            date_initial = datetime.strptime(st.selectbox("Choose a date from the dropdown below:",filtered_dates_for_initial_date_input, index=filtered_dates_for_initial_date_input.index(initial_date_str) if initial_date_str in filtered_dates_for_initial_date_input else 0), "%Y-%m-%d")
            #initial_date_str = date_initial
      
        with date_final:
            filtered_dates_for_final_date_input = [date for date in datasets if date > initial_date_str]
            st.markdown("<h4 style=' text-decoration: underline;'>Select a Final Date:</h4>", unsafe_allow_html=True)
            date_final = datetime.strptime(st.selectbox("Choose a final date from the dropdown below:",[date for date in filtered_dates_for_final_date_input]), "%Y-%m-%d")
        
        with company_intial:
            st.markdown("<h4 style=' text-decoration: underline;'>Select Company 01:</h4>", unsafe_allow_html=True)
            company_selected = st.selectbox("Choose a Company from the dropdown below:",list_of_companies)  


        with second_company:
            st.markdown("<h4 style=' text-decoration: underline;'>Select Company 02:</h4>", unsafe_allow_html=True)
            second_company_selected = st.selectbox("Choose a second Company for comparison:",list_of_companies, index=2)

        with harm_intial:
            st.markdown("<h4 style=' text-decoration: underline;'>Select a Specific Harm:</h4>", unsafe_allow_html=True)

           # Create a cleaned version of the harm list (remove prefix and underscores)
            Cleaned_harms = [harm.replace("STATEMENT_CATEGORY_", "").replace("_", " ") for harm in list_of_harms]
            # Create a mapping dictionary to match selections back to the original list
            harm_mapping = {cleaned: original for cleaned, original in zip(Cleaned_harms, list_of_harms)}
            # Streamlit selectbox with cleaned harm names
            harm_selected_cleaned = st.selectbox("Choose a Harm from the dropdown below:", Cleaned_harms)
            # Map back to the original harm category
            harm_selected = harm_mapping[harm_selected_cleaned]
            # Display the selected values for debugging or confirmation
            #print(f"Selected (Cleaned): {harm_selected_cleaned}")
           # print(f"Mapped to Original: {harm_selected}")



           # harm_selected = st.selectbox("Choose a Harm from the dropdown below:",list_of_harms)




    elif selected_option == "Evaluate two harm categories for the company":
        second_company_selected = None
        #st.write("You selected 'Harm'.")
        date_initial, date_final, company_intial, harm_intial, second_harm = st.columns(5)


        with date_initial:
            #Filter the datasets to only include dates that are less than or equal to the initial date for the initial date input and the same but opposite for final input
            filtered_dates_for_initial_date_input = [date for date in datasets if date <= initial_date_str]
            st.markdown("<h4 style=' text-decoration: underline;'>Select an Inital Date:</h4>", unsafe_allow_html=True) 
            date_initial = datetime.strptime(st.selectbox("Choose a date from the dropdown below:",filtered_dates_for_initial_date_input, index=filtered_dates_for_initial_date_input.index(initial_date_str) if initial_date_str in filtered_dates_for_initial_date_input else 0), "%Y-%m-%d")
            
        with date_final:
            filtered_dates_for_final_date_input = [date for date in datasets if date > initial_date_str]
            st.markdown("<h4 style=' text-decoration: underline;'>Select a Final Date:</h4>", unsafe_allow_html=True)
            date_final = datetime.strptime(st.selectbox("Choose a final date from the dropdown below:",[date for date in filtered_dates_for_final_date_input]), "%Y-%m-%d")
        
        with company_intial:
            st.markdown("<h4 style=' text-decoration: underline;'>Select a Company:</h4>", unsafe_allow_html=True)
            company_selected = st.selectbox("Choose a Company from the dropdown below:",list_of_companies)  

        with harm_intial:
            st.markdown("<h4 style=' text-decoration: underline;'>Select Harm 01:</h4>", unsafe_allow_html=True)

            # Create a cleaned version of the harm list (remove prefix and underscores)
            Cleaned_harms = [harm.replace("STATEMENT_CATEGORY_", "").replace("_", " ") for harm in list_of_harms]
            # Create a mapping dictionary to match selections back to the original list
            harm_mapping = {cleaned: original for cleaned, original in zip(Cleaned_harms, list_of_harms)}
            # Streamlit selectbox with cleaned harm names
            harm_selected_cleaned = st.selectbox("Choose a Harm from the dropdown below:", Cleaned_harms)
            # Map back to the original harm category
            harm_selected = harm_mapping[harm_selected_cleaned]
            # Display the selected values for debugging or confirmation
            #print(f"Selected (Cleaned): {harm_selected_cleaned}")
           # print(f"Mapped to Original: {harm_selected}")

            #harm_selected = st.selectbox("Choose a Harm from the dropdown below:",list_of_harms)

        with second_harm:
            st.markdown("<h4 style=' text-decoration: underline;'>Select Harm 02:</h4>", unsafe_allow_html=True)


            # Create a cleaned version of the harm list (remove prefix and underscores)
            Cleaned_harms = [harm.replace("STATEMENT_CATEGORY_", "").replace("_", " ") for harm in list_of_harms]
            # Create a mapping dictionary to match selections back to the original list
            harm_mapping = {cleaned: original for cleaned, original in zip(Cleaned_harms, list_of_harms)}
            # Streamlit selectbox with cleaned harm names
            harm_selected_cleaned = st.selectbox("Choose a second Harm from the dropdown below:", Cleaned_harms,index=2)
            # Map back to the original harm category
            second_harm_selected = harm_mapping[harm_selected_cleaned]
            # Display the selected values for debugging or confirmation
           # print(f"Selected (Cleaned): {harm_selected_cleaned}")
           # print(f"Mapped to Original: {second_harm_selected}")


           # second_harm_selected = st.selectbox("Choose a second Harm for comparison:",list_of_harms,index=2)

        
    else:
        second_company_selected = None
        second_harm_selected = None
        date_initial, date_final, company_intial, harm_intial = st.columns(4)

        with date_initial:
            #Filter the datasets to only include dates that are less than or equal to the initial date for the initial date input and the same but opposite for final input
            filtered_dates_for_initial_date_input = [date for date in datasets if date <= initial_date_str]
        # print("DFFII", filtered_dates_for_initial_date_input)
            st.markdown("<h4 style=' text-decoration: underline;'>Select an Inital Date:</h4>", unsafe_allow_html=True) 
            date_initial = datetime.strptime(st.selectbox("Choose a date from the dropdown below:",filtered_dates_for_initial_date_input, index=filtered_dates_for_initial_date_input.index(initial_date_str) if initial_date_str in filtered_dates_for_initial_date_input else 0), "%Y-%m-%d")
            
        with date_final:
            filtered_dates_for_final_date_input = [date for date in datasets if date > date_initial.strftime("%Y-%m-%d")]
        #  print("FDFFI", filtered_dates_for_final_date_input) 
            st.markdown("<h4 style=' text-decoration: underline;'>Select a Final Date:</h4>", unsafe_allow_html=True)
            date_final = datetime.strptime(st.selectbox("Choose a final date from the dropdown below:",[date for date in filtered_dates_for_final_date_input]), "%Y-%m-%d")
        
        with company_intial:
            st.markdown("<h4 style=' text-decoration: underline;'>Select a Company:</h4>", unsafe_allow_html=True)
            company_selected = st.selectbox("Choose a Company from the dropdown below:",list_of_companies)  

        with harm_intial:
            st.markdown("<h4 style=' text-decoration: underline;'>Select a Specific Harm:</h4>", unsafe_allow_html=True)

            # Create a cleaned version of the harm list (remove prefix and underscores)
            Cleaned_harms = [harm.replace("STATEMENT_CATEGORY_", "").replace("_", " ") for harm in list_of_harms]
            # Create a mapping dictionary to match selections back to the original list
            harm_mapping = {cleaned: original for cleaned, original in zip(Cleaned_harms, list_of_harms)}
            # Streamlit selectbox with cleaned harm names
            harm_selected_cleaned = st.selectbox("Choose a Harm from the dropdown below:", Cleaned_harms)
            # Map back to the original harm category
            harm_selected = harm_mapping[harm_selected_cleaned]
            # Display the selected values for debugging or confirmation
           # print(f"Selected (Cleaned): {harm_selected_cleaned}")
           # print(f"Mapped to Original: {harm_selected}")

            
            #harm_selected = st.selectbox("Choose a Harm from the dropdown below:",list_of_harms)

        



      
    ##############################################################################################################  --- Historical data GRAPHS CREATION --- ###############################################################################################################
    
    #getting all the dates between the user chosen initial date and final date
    all_dates_between_initial_final_dates = [(date_initial + timedelta(days=i)).strftime("%Y-%m-%d")  for i in range((date_final - date_initial).days + 1) if (date_initial + timedelta(days=i)).strftime("%Y-%m-%d") in datasets]

#dataet loaded plot 1 2
#dataset loaded 2 for plot 3 adn 4

    def append_historical1(date):
        return f"{date}_historical1"
    
    def append_historical2(date):
        return f"{date}_historical2"

    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        updated_dates = list(executor.map(append_historical1, all_dates_between_initial_final_dates))
        datasets_loaded = list(executor.map(load_data, updated_dates))
   

    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        updated_dates2 = list(executor.map(append_historical2, all_dates_between_initial_final_dates))
        datasets_loaded2 = list(executor.map(load_data, updated_dates2))
  


    ####################################################
    # Process the loaded data above

    #if two companies are selected

    if second_company_selected is not None:
        print("data used is two companies")

        def process_data(data):
            #for company 1
            return plot_acc_totals_per_harm_company_harm_historical_orig(data, company_selected, harm_selected)
        

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_data, datasets_loaded))
            results2 = list(executor.map(process_data, datasets_loaded2))

            # print("results for first company ", results)
            # print("results2 for first company", results2)
            # print("---")


         #-------------------------------------
        # Repeat the process with your second set of data #for company 2

        def process_data_second(data):
            return plot_acc_totals_per_harm_company_harm_historical_orig(data, second_company_selected, harm_selected)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results_second_company_selected = list(executor.map(process_data_second, datasets_loaded))
            results2_second_company_selected = list(executor.map(process_data_second, datasets_loaded2))

            # print("results_second_company_selected", results_second_company_selected)
            # print("results2_second_company_selected", results2_second_company_selected)




    #if a second harm is selected
    elif second_harm_selected is not None:
        print("data used its trwo harms")
    
        def process_data(data):
            #for company 1
            return plot_acc_totals_per_harm_company_harm_historical_orig(data, company_selected, harm_selected)
        

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_data, datasets_loaded))
            results2 = list(executor.map(process_data, datasets_loaded2))


         #-------------------------------------
        # Repeat the process with your second set of data #for harm 2

        def process_data_second(data):
            return plot_acc_totals_per_harm_company_harm_historical_orig(data, company_selected, second_harm_selected)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results_second_harm_selected = list(executor.map(process_data_second, datasets_loaded))
            results2_second_harm_selected = list(executor.map(process_data_second, datasets_loaded2))




    #if two harms or two companies are NOT selected (default option none)
    else:
        print("data used is 1 harm and 1 company")
        #Ffor one company and one harm only
        def process_data(data):
            return plot_acc_totals_per_harm_company_harm_historical_orig(data, company_selected, harm_selected)
    

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_data, datasets_loaded))
            results2 = list(executor.map(process_data, datasets_loaded2))

        
    ####################################################


    ####################################################
    #graph creation for two companies
    if second_company_selected is not None:

        df_company_1 = pd.DataFrame({
        'Dates': all_dates_between_initial_final_dates,
        'Automated': [result[0] for result in results],
        'Manual': [result[1] for result in results],
        'Company': company_selected
        })

        df_company_2 = pd.DataFrame({
            'Dates': all_dates_between_initial_final_dates,
            'Automated': [result[0] for result in results_second_company_selected],
            'Manual': [result[1] for result in results_second_company_selected],
            'Company': second_company_selected
        })
        
        

        df_combined = pd.concat([df_company_1.melt(['Dates', 'Company'], var_name='Type', value_name='DAILY FLAGGED CONTENT'),
                                df_company_2.melt(['Dates', 'Company'], var_name='Type', value_name='DAILY FLAGGED CONTENT')])

        chart = alt.Chart(df_combined).mark_line().encode(
            x='Dates:T',
            y='DAILY FLAGGED CONTENT:Q',
            color=alt.Color('Type:N', scale=alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])),
            strokeDash='Company:N'
        ).properties(
            title='Comparison of ACC Flag Count for Two Companies'
        )


        #second chart
        acc_total_1 = df_company_1['Automated'].sum()
        user_total_1 = df_company_1['Manual'].sum()

        acc_total_2 = df_company_2['Automated'].sum()
        user_total_2 = df_company_2['Manual'].sum()

        # Create a DataFrame with the totals for both companies
        data_totals = {
            'Category': ['Automated', 'Manual', 'Automated', 'Manual'],
            'Total Harm Count': [acc_total_1, user_total_1, acc_total_2, user_total_2],
            'Company': [company_selected, company_selected, second_company_selected, second_company_selected]
        }

        df_totals = pd.DataFrame(data_totals)

        color_scale = alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])

        # Create an Altair grouped bar chart with company text labels
        bars = alt.Chart(df_totals).mark_bar().encode(
            x=alt.X('Category:N', title='', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Total Harm Count:Q', title='TOTAL FLAGGED CONTENT'),
            color=alt.Color('Category:N', scale=color_scale, legend=None),
            xOffset='Company:N'  # This groups the bars by company
        )

        # Add text labels for the companies above the bars
        text = alt.Chart(df_totals).mark_text(dy=-15, fontSize=12, color='black').encode(
            x=alt.X('Category:N', title='', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Total Harm Count:Q', title='TOTAL FLAGGED CONTENT'),
            detail='Company:N',
            text=alt.Text('Company:N'),
            xOffset='Company:N'
        )

        chart_two = (bars + text).properties(
            width=300
        )



        #third chart
        # Moderation time graph for two companies
        df_company_1 = pd.DataFrame({
            'Dates': all_dates_between_initial_final_dates,
            'Automated': [result[0] / 60 for result in results2],
            'Manual': [result[1] / 60 for result in results2],
            'Company': company_selected
        })

        # Ensure there are no division by zero errors for company 1
        df_company_1['Automated'] = df_company_1['Automated'] / pd.Series([result[0] for result in results]).replace(0, pd.NA)
        df_company_1['Manual'] = df_company_1['Manual'] / pd.Series([result[1] for result in results]).replace(0, pd.NA)
        df_company_1 = df_company_1.fillna(0)

        df_company_2 = pd.DataFrame({
            'Dates': all_dates_between_initial_final_dates,
            'Automated': [result[0] / 60 for result in results2_second_company_selected],
            'Manual': [result[1] / 60 for result in results2_second_company_selected],
            'Company': second_company_selected
        })

        # Ensure there are no division by zero errors for company 2
        df_company_2['Automated'] = df_company_2['Automated'] / pd.Series([result[0] for result in results_second_company_selected]).replace(0, pd.NA)
        df_company_2['Manual'] = df_company_2['Manual'] / pd.Series([result[1] for result in results_second_company_selected]).replace(0, pd.NA)
        df_company_2 = df_company_2.fillna(0)

        # Combine both companies
        df_combined = pd.concat([df_company_1.melt(['Dates', 'Company'], var_name='Type', value_name='MODERATION TIME (HRS)'),
                                df_company_2.melt(['Dates', 'Company'], var_name='Type', value_name='MODERATION TIME (HRS)')])

        # Create an Altair chart for two companies
        chart_three = alt.Chart(df_combined).mark_line().encode(
            x='Dates:T',
            y='MODERATION TIME (HRS):Q',
            color=alt.Color('Type:N', scale=alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])),
            strokeDash='Company:N'
        ).properties(
            title='ACC VS Manual Moderation Time (Detection + Decision Periods) for Two Companies'
        )



        
        #graph4
        #fix the values not correct (think), alyout is working
        # ---------------------------------------------------------------------------------------------------

        # If you want to avoid NaN values after division, you can use a fill method:

        acc_total4 = df_company_1['Automated'][df_company_1['Automated'] != 0].mean()
        user_total4 = df_company_1['Manual'][df_company_1['Manual'] != 0].mean()

        acc_total4_second = df_company_2['Automated'][df_company_2['Automated'] != 0].mean()
        user_total4_second = df_company_2['Manual'][df_company_2['Manual'] != 0].mean()
        
        
        acc_total4 = 0 if pd.isna(acc_total4) else acc_total4
        user_total4 = 0 if pd.isna(user_total4) else user_total4
        acc_total4_second = 0 if pd.isna(acc_total4_second) else acc_total4_second
        user_total4_second = 0 if pd.isna(user_total4_second) else user_total4_second
        


        # Create DataFrame with the totals for both companies
        df_totals = pd.DataFrame({
            'Category': ['Automated', 'Manual', 'Automated', 'Manual'],
            'Average Moderation Time (Hrs)': [acc_total4, user_total4, acc_total4_second, user_total4_second],
            'Company': [company_selected, company_selected, second_company_selected, second_company_selected]
        })

        # Define color scale for Automated vs Manual
        color_scale = alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])

        # Create a grouped bar chart with company offset
        bars = alt.Chart(df_totals).mark_bar().encode(
            x=alt.X('Category:N', title='', axis=alt.Axis(labelAngle=0)),  # Categories (Automated, Manual)
            y=alt.Y('Average Moderation Time (Hrs):Q', title='AVERAGE MODERATION TIME (HRS)'),  # Total harm count on Y-axis
            color=alt.Color('Category:N', scale=color_scale, legend=None),  # Color by Automated/Manual
            xOffset='Company:N'  # Offset bars by Company (ensures grouping)
        )

        # Add text labels above bars showing company names
        text = alt.Chart(df_totals).mark_text(dy=-15, fontSize=12, color='black').encode(
        x=alt.X('Category:N', title='', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Average Moderation Time (Hrs):Q', title='AVERAGE MODERATION TIME (HRS)'),
        text=alt.Text('Company:N'),  # Display company name
        xOffset='Company:N'  # Align text with corresponding bars
    )

        # Combine bars and text
        chart_four = (bars + text).properties(
            width=300
        )
                
        # ---------------------------------------------------------------------------------------------------





    #graph creation for two harms
    elif second_harm_selected is not None:


        harm_selected_label = category_descriptions.get(harm_selected, harm_selected)
        second_harm_selected_label = category_descriptions.get(second_harm_selected, second_harm_selected)

        #first chart
        df_company_1 = pd.DataFrame({
        'Dates': all_dates_between_initial_final_dates,
        'Automated': [result[0] for result in results],
        'Manual': [result[1] for result in results],
        'Harm': harm_selected_label
        })

        df_company_2 = pd.DataFrame({
            'Dates': all_dates_between_initial_final_dates,
            'Automated': [result[0] for result in results_second_harm_selected],
            'Manual': [result[1] for result in results_second_harm_selected],
            'Harm': second_harm_selected_label
        })

        print("original DF2", df_company_2)

        df_combined = pd.concat([df_company_1.melt(['Dates', 'Harm'], var_name='Type', value_name='DAILY FLAGGED CONTENT'),
                                df_company_2.melt(['Dates', 'Harm'], var_name='Type', value_name='DAILY FLAGGED CONTENT')])

        chart = alt.Chart(df_combined).mark_line().encode(
            x='Dates:T',
            y='DAILY FLAGGED CONTENT:Q',
            color=alt.Color('Type:N', scale=alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])),
            strokeDash='Harm:N'
        ).properties(
            title='Comparison of ACC Flag Count for Two Harms'
        )


        #second chart
        acc_total_1_harm = df_company_1['Automated'].sum()
        user_total_1_harm = df_company_1['Manual'].sum()

        acc_total_2_harm= df_company_2['Automated'].sum()
        user_total_2_harm = df_company_2['Manual'].sum()

        # Create a DataFrame with the totals for both companies
        data_totals = {
            'Category': ['Automated', 'Manual', 'Automated', 'Manual'],
            'Total Harm Count': [acc_total_1_harm, user_total_1_harm, acc_total_2_harm, user_total_2_harm],
            'Harm': [harm_selected_label, harm_selected_label, second_harm_selected_label, second_harm_selected_label]
        }

        df_totals = pd.DataFrame(data_totals)

        color_scale = alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])

        # Create an Altair grouped bar chart with company text labels
        bars = alt.Chart(df_totals).mark_bar().encode(
            x=alt.X('Category:N', title='', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Total Harm Count:Q', title='TOTAL FLAGGED CONTENT'),
            color=alt.Color('Category:N', scale=color_scale, legend=None),
            xOffset='Harm:N'  # This groups the bars by company
        )

        # Add text labels for the companies above the bars
        text = alt.Chart(df_totals).mark_text(dy=-15, fontSize=12, color='black').encode(
            x=alt.X('Category:N', title='', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Total Harm Count:Q', title='TOTAL FLAGGED CONTENT'),
            detail='Harm:N',
            text=alt.Text('Harm:N'),
            xOffset='Harm:N'
        )

        chart_two = (bars + text).properties(
            width=300
        )



        #third chart
        # Moderation time graph for two companies
        df_company_1 = pd.DataFrame({
            'Dates': all_dates_between_initial_final_dates,
            'Automated': [result[0] / 60 for result in results2],
            'Manual': [result[1] / 60 for result in results2],
            'Harm': harm_selected_label
        })

        # Ensure there are no division by zero errors for company 1
        df_company_1['Automated'] = df_company_1['Automated'] / pd.Series([result[0] for result in results]).replace(0, pd.NA)
        df_company_1['Manual'] = df_company_1['Manual'] / pd.Series([result[1] for result in results]).replace(0, pd.NA)
        df_company_1 = df_company_1.fillna(0)
        
        print("DF1 third chart", df_company_1)
        
        

        df_company_2 = pd.DataFrame({
            'Dates': all_dates_between_initial_final_dates,
            'Automated': [result[0] / 60 for result in results2_second_harm_selected],
            'Manual': [result[1] / 60 for result in results2_second_harm_selected],
            'Harm': second_harm_selected_label
        })

        # Ensure there are no division by zero errors for company 2
        df_company_2['Automated'] = df_company_2['Automated'] / pd.Series([result[0] for result in results_second_harm_selected]).replace(0, pd.NA)
        df_company_2['Manual'] = df_company_2['Manual'] / pd.Series([result[1] for result in results_second_harm_selected]).replace(0, pd.NA)
        df_company_2 = df_company_2.fillna(0)

        # Combine both companies
        df_combined = pd.concat([df_company_1.melt(['Dates', 'Harm'], var_name='Type', value_name='MODERATION TIME (HRS)'),
                                df_company_2.melt(['Dates', 'Harm'], var_name='Type', value_name='MODERATION TIME (HRS)')])

        # Create an Altair chart for two companies
        chart_three = alt.Chart(df_combined).mark_line().encode(
            x='Dates:T',
            y='MODERATION TIME (HRS):Q',
            color=alt.Color('Type:N', scale=alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])),
            strokeDash='Harm:N'
        ).properties(
            title='ACC VS Manual Moderation Time (Detection + Decision Periods) for Two Harms'
        )




        #graph4

        # Calculate averages for one company
        #working layout not just need to fix values
    
        

        # Process Data: Compute average moderation time (in hours) for both harms
        acc_total4 = df_company_1['Automated'][df_company_1['Automated'] != 0].mean()
        user_total4 = df_company_1['Manual'][df_company_1['Manual'] != 0].mean()
        

        acc_total4_second = df_company_2['Automated'][df_company_2['Automated'] != 0].mean()
        user_total4_second = df_company_2['Manual'][df_company_2['Manual'] != 0].mean()
        
        acc_total4 = 0 if pd.isna(acc_total4) else acc_total4
        user_total4 = 0 if pd.isna(user_total4) else user_total4
        acc_total4_second = 0 if pd.isna(acc_total4_second) else acc_total4_second
        user_total4_second = 0 if pd.isna(user_total4_second) else user_total4_second
        

        # Create DataFrame for visualization
        df_bar = pd.DataFrame({
            'Category': ['Automated', 'Manual', 'Automated', 'Manual'],
            'Average Moderation Time (Hrs)': [acc_total4, user_total4, acc_total4_second, user_total4_second],
            'Harm': [harm_selected_label, harm_selected_label, second_harm_selected_label, second_harm_selected_label]
        })

        # Define color scale
        color_scale = alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])

        # Create grouped bar chart (Harm as main category, with separate Automated & Manual bars)
        chart_four = alt.Chart(df_bar).mark_bar().encode(
            x=alt.X('Harm:N', title='Harm Type', axis=alt.Axis(labelAngle=0)),  # Harm types on x-axis
            y=alt.Y('Average Moderation Time (Hrs):Q', title='AVERAGE MODERATION TIME (HRS)'),  # Moderation time on y-axis
            color=alt.Color('Category:N', scale=color_scale, legend=alt.Legend(title="Moderation Type")),  # Color for Automated & Manual
            xOffset='Category:N',  # Offsets bars to group by Harm type
            tooltip=['Category', 'Average Moderation Time (Hrs)', 'Harm']
        ).properties(
            width=300
        )




    #graph creation for default (none)
    else:

        #graph1
        df = pd.DataFrame({
            'Dates': all_dates_between_initial_final_dates,
            'Automated': [result[0] for result in results],
            'Manual': [result[1] for result in results]
        })

        # Melt the DataFrame to a long format for Altair
        df_long = df.melt('Dates', var_name='Type', value_name='DAILY FLAGGED CONTENT')

        # Create an Altair chart
        chart = alt.Chart(df_long).mark_line().encode(
            x='Dates',
            y='DAILY FLAGGED CONTENT',
            color=alt.Color('Type', scale=alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])),
            strokeDash='Type'
        ).properties(
            title='ACC Flag count vs User Flag count'
        )



        #graph2
        acc_total = df['Automated'].sum()
        user_total = df["Manual"].sum()
        # Create a DataFrame with the totals
        data_a = {'Category': ['Automated', 'Manual'],'Total Harm Count': [acc_total, user_total]}
        df_xx = pd.DataFrame(data_a)
        color_scale = alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])
        # Create an Altair bar chart
        # Create an Altair bar chart with a title
        
        chart_two = alt.Chart(df_xx).mark_bar().encode(
        x=alt.X('Category:N', title=''),
        y=alt.Y('Total Harm Count:Q', title='TOTAL FLAGGED CONTENT'),
        color=alt.Color('Category:N', scale=color_scale, legend=None)
    ).properties(
        width=alt.Step(80)
    )


        #graph3 one company
        # #GRAPH #3
        df_three = pd.DataFrame({
            'Dates': all_dates_between_initial_final_dates,
            'Automated': [result[0] / 60 for result in results2],
            'Manual': [result[1] / 60 for result in results2]
        })

        # Ensure there are no division by zero errors
        df_three['Automated'] = df_three['Automated'] / df['Automated'].replace(0, pd.NA)
        df_three['Manual'] = df_three['Manual'] / df['Manual'].replace(0, pd.NA)

        # If you want to avoid NaN values after division, you can use a fill method:
        df_three['Automated'] = df_three['Automated'].fillna(0)
        df_three['Manual'] = df_three['Manual'].fillna(0)


        # Melt the dataframe to a long format for Altair
        df_long = df_three.melt('Dates', var_name='Type', value_name='MODERATION TIME (HRS)')
        # Create an Altair chart
        chart_three = alt.Chart(df_long).mark_line().encode(
            x='Dates',
            y='MODERATION TIME (HRS)',
            color=alt.Color('Type', scale=alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])),
            strokeDash='Type').properties(
            title='ACC VS Manual Moderation Time (Detection + Decision Periods)')

       #grph 4 values showing correct
       # ---------------------------------------------------------------------------------------------------


        #graph4
        acc_total4 = df_three['Automated'][df_three['Automated'] != 0].mean()
        user_total4 = df_three['Manual'][df_three['Manual'] != 0].mean()

        if pd.isna(acc_total4):
            acc_total4 = 0

        if pd.isna(user_total4):
            user_total4 = 0


        data_a = {'Category': ['Automated', 'Manual'],'Total Harm Count': [int(acc_total4), int(user_total4)]}
        df_xx = pd.DataFrame(data_a)
        color_scale = alt.Scale(domain=['Automated', 'Manual'], range=['red', 'green'])
        # Create an Altair bar chart with a title
        chart_four = alt.Chart(df_xx).mark_bar().encode(
            x=alt.X('Category:N', title=''),
            y=alt.Y('Total Harm Count:Q', title='AVERAGE MODERATION TIME (HRS)'),
            color=alt.Color('Category:N', scale=color_scale, legend=None)
        ).properties(
            width=alt.Step(80)
        )
            

        

    # ####################################################

    #Plotting the graphs made above
    col1, col2 = st.columns(2)
    
    with col1:
        st.altair_chart(chart, use_container_width=True)

    with col2:

        
       try:
            # Try using acc_total and user_total
            formatted_number1 = format(int(acc_total), ",")
            formatted_number2 = format(int(user_total), ",")
            
            st.write(
                f"<span style='color:red; font-weight:bold;'>Automated</span> (ACC): {formatted_number1} ┃ "
                f"<span style='color:green; font-weight:bold;'>Manual</span> (User reported): {formatted_number2}",
                unsafe_allow_html=True
            )

            st.altair_chart(chart_two, use_container_width=True)

       except NameError:
            try:
                # If acc_total doesn't exist, use acc_total_1 and acc_total_2
                formatted_number1 = format(int(acc_total_1), ",")
                formatted_number2 = format(int(user_total_1), ",")
                formatted_number3 = format(int(acc_total_2), ",")
                formatted_number4 = format(int(user_total_2), ",")

                st.write(
                f"<span style='color:red; font-weight:bold;'>Automated</span> ({company_selected}): {formatted_number1} ┃ "
                f"<span style='color:green; font-weight:bold;'>Manual</span> ({company_selected}): {formatted_number2} || "
                f"<span style='color:red; font-weight:bold;'>Automated</span> ({second_company_selected}): {formatted_number3} ┃ "
                f"<span style='color:green; font-weight:bold;'>Manual</span> ({second_company_selected}): {formatted_number4}",
                unsafe_allow_html=True
            )

            except NameError:
                # If acc_total_1 doesn't exist, use acc_total_1_harm and user_total_1_harm
                formatted_number1 = format(int(acc_total_1_harm), ",")
                formatted_number2 = format(int(user_total_1_harm), ",")
                formatted_number3 = format(int(acc_total_2_harm), ",")
                formatted_number4 = format(int(user_total_2_harm), ",")

                st.write(
                f"<span style='font-size:14px;'>"
                    f"<span style='color:red; font-weight:bold;'>Automated</span> ({harm_selected_label}): {formatted_number1} ┃ "
                    f"<span style='color:green; font-weight:bold;'>Manual</span> ({harm_selected_label}): {formatted_number2} | "
                    f"<span style='color:red; font-weight:bold;'>Automated</span> ({second_harm_selected_label}): {formatted_number3} ┃ "
                    f"<span style='color:green; font-weight:bold;'>Manual</span> ({second_harm_selected_label}): {formatted_number4}",
                    f"</span>",
                    unsafe_allow_html=True
                )

        # Display the chart
            st.altair_chart(chart_two, use_container_width=True)





    
    with col1:
        st.altair_chart(chart_three, use_container_width=True)
    with col2:
        
        def format_time(value):
            return f"{value:.0f} Hrs" if value <= 24 else f"{(value / 24):.1f} Days"
        
        if company_selected and second_company_selected:
            st.write(
                f"<span style='font-size:14px;'>"
                f"<span style='color:red; font-weight:bold;'>Automated</span> ({company_selected}): {format_time(acc_total4)} ┃ "
                f"<span style='color:green; font-weight:bold;'>Manual</span> ({company_selected}): {format_time(user_total4)} ┃ "
                f"<span style='color:red; font-weight:bold;'>Automated</span> ({second_company_selected}): {format_time(acc_total4_second)} ┃ "
                f"<span style='color:green; font-weight:bold;'>Manual</span> ({second_company_selected}): {format_time(user_total4_second)} "
                f"</span>",
                unsafe_allow_html=True
            )
        
        elif harm_selected and second_harm_selected:
            # Get the readable category descriptions
            harm_selected_label = category_descriptions.get(harm_selected, harm_selected)
            second_harm_selected_label = category_descriptions.get(second_harm_selected, second_harm_selected)

            st.write(
                f"<span style='font-size:14px;'>"
                f"<span style='color:red; font-weight:bold;'>Automated</span> ({harm_selected_label}): {format_time(acc_total4)} ┃ "
                f"<span style='color:green; font-weight:bold;'>Manual</span> ({harm_selected_label}): {format_time(user_total4)} ┃ "
                f"<span style='color:red; font-weight:bold;'>Automated</span> ({second_harm_selected_label}): {format_time(acc_total4_second)} ┃ "
                f"<span style='color:green; font-weight:bold;'>Manual</span> ({second_harm_selected_label}): {format_time(user_total4_second)} "
                f"</span>",
                unsafe_allow_html=True
            )
        
        elif company_selected and harm_selected:
            harm_version = category_descriptions.get(harm_selected, "UNKNOWN HARM")
            st.write(
                f"<span style='font-size:14px;'>"
                f"<span style='color:red; font-weight:bold;'>Automated Results: </span> {format_time(acc_total4)} ┃ "
                f"<span style='color:green; font-weight:bold;'>Manual Results:</span> {format_time(user_total4)} ┃ "
                f"<span style='color:green; font-weight:bold;'>For:</span> {company_selected} & {harm_version}"
                f"</span>",
                unsafe_allow_html=True
            )
        else:
            st.write("Error: No valid company or harm data available.")
        
        st.altair_chart(chart_four, use_container_width=True)
























############################################################################################################################################################################################################################################################
############################################################################################################################################################################################################################################################
##############################################################################################################  --- DAILY LIVE ANALYSIS  --- ###############################################################################################################

    ####################################################
    # Columns, Titles and dataset selectbox
    st.write('<h2 style="text-align: center; text-decoration: underline;">Daily Live Analysis</h2>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-decoration: underline;'>Select a Specific Date</h3>", unsafe_allow_html=True)
    selected_dataset = st.selectbox("Choose a Date:", datasets)
    general_data_col, company_col, harm_col = st.columns(3)
    
    ####################################################


    ####################################################
    # Load data and extract lists from the selected dataset
    if selected_dataset:
        data, List_of_companies, List_of_harms, List_of_content_type, List_of_moderation_action, List_of_automation_status = load_data_from_dataset(selected_dataset + ".pkl")
        #load_data_from_dataset(selected_dataset + ".pkl")
    ####################################################


    ####################################################
    #making the user selection columns
    with general_data_col:
        st.markdown("<h3 style='text-decoration: underline;'>Overall Info for All Companies</h3>", unsafe_allow_html=True)
        selected_option_gen = st.checkbox("General Data")
        disable_others = selected_option_gen  # Disable other options if general data is selected

    with company_col:
        st.markdown("<h3 style='text-decoration: underline;'>Select a Specific Company</h3>", unsafe_allow_html=True)
        selected_company = st.selectbox("Choose a Company:", [None] + List_of_companies, disabled=disable_others)

    # with harm_col:
    #      st.markdown("<h3 style='text-decoration: underline;'>Select a Specific Harm</h3>", unsafe_allow_html=True)
    #      selected_harm = st.selectbox("Choose a Harm:", [None] + List_of_harms, disabled=disable_others)

    with harm_col:
        st.markdown("<h3 style='text-decoration: underline;'>Select a Specific Harm</h3>", unsafe_allow_html=True)
        
        category_descriptionssss = {
            'STATEMENT_CATEGORY_SCOPE_OF_PLATFORM_SERVICE': 'PLATFORM SCOPE',
            'STATEMENT_CATEGORY_DATA_PROTECTION_AND_PRIVACY_VIOLATIONS': 'GDPR VIOLATION',
            'STATEMENT_CATEGORY_PORNOGRAPHY_OR_SEXUALIZED_CONTENT': 'PORN/SEX CONTENT',
            'STATEMENT_CATEGORY_ILLEGAL_OR_HARMFUL_SPEECH': 'ILLEGAL/HARMFUL SPEECH',
            'STATEMENT_CATEGORY_VIOLENCE': 'VIOLENCE',
            'STATEMENT_CATEGORY_SCAMS_AND_FRAUD': 'SCAMS/FRAUD',
            'STATEMENT_CATEGORY_UNSAFE_AND_ILLEGAL_PRODUCTS': 'ILLEGAL PRODUCTS',
            'STATEMENT_CATEGORY_NON_CONSENSUAL_BEHAVIOUR': 'NON-CONSENSUAL BEHAVIOUR',
            'STATEMENT_CATEGORY_PROTECTION_OF_MINORS': 'PROTECT MINORS',
            'STATEMENT_CATEGORY_INTELLECTUAL_PROPERTY_INFRINGEMENTS': 'COPYRIGHT',
            'STATEMENT_CATEGORY_NEGATIVE_EFFECTS_ON_CIVIC_DISCOURSE_OR_ELECTIONS': 'NEGATIVE EFFECTS ON ELECTIONS',
            'STATEMENT_CATEGORY_RISK_FOR_PUBLIC_SECURITY': 'RISK TO PUBLIC SECURITY',
            'STATEMENT_CATEGORY_ANIMAL_WELFARE': 'ANIMAL WELFARE',
            'STATEMENT_CATEGORY_SELF_HARM': 'SELF HARM'
        }

        # Create a mapping for display
        harm_display_map = {harm: category_descriptionssss.get(harm, harm) for harm in List_of_harms}

        # Reverse mapping to get back the original harm key
        display_options = [None] + list(harm_display_map.values())
        selected_display_harm = st.selectbox("Choose a Harm:", display_options, disabled=disable_others)

        # Convert selected display harm back to its key
        selected_harm = next((key for key, value in harm_display_map.items() if value == selected_display_harm), None)



    ####################################################


    ########################################################################################################
    if selected_option_gen:
        st.markdown("---")
        st.subheader("Analysis for General Overview")
        col1, col2 = st.columns(2)
   
        fig1 = plot_acc_totals_per_company(data)
        fig2 = plot_acc_totals_per_harm(data)
        fig3 = plot_acc_totals_per_moderation_action(data)
        fig4 = plot_acc_totals_per_automation_status(data)
        fig5 = plot_acc_totals_per_content_type(data)
        fig6 = plot_acc_totals(data)
        fig7 = sum_harm(data)
        fig8 = plot_company_dataxxz(data, List_of_companies)
        fig9 = plot_company_dataxxz_normalized(data, List_of_companies)
        fig10 = plot_content_type_totals(data)
        fig11 = plot_moderation_action_totals(data)
        fig12 = plot_automation_status_totals(data)
        fig13 = plot_harm_totals_per_company(data)
        fig14 = plot_content_type_totals_per_company(data)
        fig15 = plot_automation_status_table_general(data)
        fig16 = plot_normalized_automation_status(data)
        fig17 = plot_harm_content_type(data)
        fig18 = plot_harm_content_type_normalized(data)
        fig19 = plot_harm_automation_status(data)
        fig20 = plot_harm_automation_status_two(data)
        fig21 = plot_content_type_automation_status(data)
        fig22 = plot_content_type_automation_status_two(data)
        fig23 = sum_reports_per_harm_per_moderation_action(data)
        fig24 = generate_moderation_action_automation_status_figure(data)
        fig25 = sum_reports_per_moderation_action_per_company(data)

        with col1:
            with st.expander("Analysis of Moderation Actions vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig3, use_container_width=True)

                csv = fig3.to_csv(index=False)
    
                # Add a download button
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='moderation_data.csv',
                    mime='text/csv',
                )
        with col2:
            with st.expander("Analysis of Type of Moderation vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig4, use_container_width=True)
        with col1:
            with st.expander("Analysis of Content Type vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig5, use_container_width=True)
        with col2:
            with st.expander("Analysis of Company vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig1, use_container_width=True)
        with col1:
            with st.expander("Analysis of Harm Category vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig2, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Detection Type (User vs. Automated)", expanded=False):
                st.dataframe(fig6, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Harm Category", expanded=False):
                st.dataframe(fig7, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Company", expanded=False):
                st.dataframe(fig8, use_container_width=True)          
        with col1:
            with st.expander("Total Moderated Content per Company", expanded=False):
                st.dataframe(fig9, use_container_width=True)     
        with col2:
            with st.expander("Total Moderated Content per Type of Content", expanded=False):
                st.dataframe(fig10, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Type of Moderation", expanded=False):
                st.dataframe(fig12, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Type of Moderation Action", expanded=False):
                st.dataframe(fig11, use_container_width=True)
        with col1:
            with st.expander(" Analysis of Harm Category vs. Company", expanded=False):
                st.dataframe(fig13, use_container_width=True)
        with col2:
            with st.expander("Analysis of Company vs. Type of Content Moderated", expanded=False):
                st.dataframe(fig14, use_container_width=True)
        with col1:
            with st.expander("Analysis of Company vs. Type of Moderation Adopted", expanded=False):
                st.dataframe(fig16, use_container_width=True)
        with col2:
            with st.expander("Analysis of Harm Category vs. Type of Content Moderated", expanded=False):
                st.dataframe(fig17, use_container_width=True)
        with col1:
            with st.expander("Analysis of Harm Category vs. Moderated Content Type", expanded=False):
                st.dataframe(fig18, use_container_width=True)               
        with col2:
            with st.expander("Analysis of Harm Category vs. Type of Moderation", expanded=False):
                st.dataframe(fig19, use_container_width=True)
        with col1:
            with st.expander("Analysis of Harm Category vs. Type of Moderation", expanded=False):
                st.dataframe(fig20, use_container_width=True)
        with col2:
            with st.expander("Analysis of Harm Category vs. Type of Moderation Action", expanded=False):
                st.dataframe(fig23, use_container_width=True)
        with col1:
            with st.expander("Analysis of Moderated Content Type vs. Type of Moderation Adopted", expanded=False):
                st.dataframe(fig21, use_container_width=True)
        with col2:
            with st.expander("Analysis of Moderated Content Type vs. Type of Moderation Adopted Normalized", expanded=False):
                st.dataframe(fig22, use_container_width=True)
        with col1:
            with st.expander("Analysis of Company vs. Moderation Actions Adopted", expanded=False):
                st.dataframe(fig25, use_container_width=True)
                
    ########################################################################################################


    ########################################################################################################
    elif selected_company and selected_harm:
        st.markdown("---")
        st.subheader(f"Analysis for {selected_company} and {selected_display_harm}")
        col1, col2 = st.columns(2)


        fig1 = plot_acc_totals_per_company_company_harm(data, selected_company, selected_harm)
        fig2 = plot_acc_totals_per_harm_company_harm(data, selected_company, selected_harm)
        fig3 = plot_acc_totals_per_moderation_action_company_harm(data, selected_company, selected_harm)
        fig4 = plot_acc_totals_per_automation_status_company_harm(data, selected_company, selected_harm)
        fig5 = plot_acc_totals_per_content_type_company_harm(data, selected_company, selected_harm)
        fig6 = plot_acc_totals_company_harm(data, selected_company, selected_harm)
        fig7 = sum_harm3(data, selected_company, selected_harm)
        fig8 = plot_company_dataxxz3(data, selected_company, selected_harm)
        fig9 = plot_company_dataxxz3_normalized(data, selected_company, selected_harm)
        fig10 = plot_content_type_totals3(data, selected_company, selected_harm)
        fig11 = plot_moderation_action_totals3(data, selected_company, selected_harm)
        fig12 = plot_automation_status_totals3(data, selected_company, selected_harm)
        fig13 = plot_harm_totals_per_company3(data, selected_company, selected_harm)
        fig14 = plot_content_type_totals_per_company3(data, selected_company, selected_harm)
        fig15 = plot_automation_status_table_general3(data, selected_company, selected_harm)
        fig16 = plot_normalized_automation_status3(data, selected_company, selected_harm)
        #fig17 = plot_harm_content_type3_normalized(data, selected_company, selected_harm)
        fig18 = plot_harm_content_type_normalized3(data, selected_company, selected_harm)
        fig19 = plot_harm_automation_status3(data, selected_company, selected_harm)
        fig20 = plot_harm_automation_status3_normalized(data, selected_company, selected_harm)
        fig21 = plot_content_type_automation_status3(data, selected_company, selected_harm)
        fig22 = plot_content_type_automation_status3_normalized(data, selected_company, selected_harm)
        fig23 = generate_moderation_action_automation_status_figure3(data, selected_company, selected_harm)
        fig24 = sum_reports_per_moderation_action_per_company3(data, selected_company, selected_harm)

        with col1:
            with st.expander("Analysis of Moderation Actions vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig3, use_container_width=True)
        with col2:
            with st.expander("Analysis of Type of Moderation vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig4, use_container_width=True)
        with col1:
            with st.expander("Analysis of Content Type vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig5, use_container_width=True)
        with col2:
            with st.expander("Analysis of Company vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig1, use_container_width=True)
        with col1:
            with st.expander("Analysis of Harm Category vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig2, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Detection Type (User vs. Automated)", expanded=False):
                st.dataframe(fig6, use_container_width=True)
        with col1:
            with st.expander("Total number of Moderation actions for selected harm and company", expanded=False):
                st.dataframe(fig7, use_container_width=True)
        with col2:
            with st.expander("Total number of Moderation Actions normalized for selected harm and company", expanded=False):
                st.dataframe(fig9, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Type of Content for selected harm and company", expanded=False):
                st.dataframe(fig10, use_container_width=True)
        with col2:
            with st.expander("Total number of Moderation Actions per Type of moderation action for selected harm and company", expanded=False):
                st.dataframe(fig11, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Type of Moderation Action for selected harm and company", expanded=False):
                st.dataframe(fig12, use_container_width=True)
        with col2:
            with st.expander("Number of reported Harms for selected harm and company", expanded=False):
                st.dataframe(fig13, use_container_width=True)
        with col1:
            with st.expander("Number of reported content type for selected harm and company", expanded=False):
                st.dataframe(fig14, use_container_width=True)
        with col2:
            with st.expander("Number of Automation Status type for selected harm and company", expanded=False):
                st.dataframe(fig15, use_container_width=True)
        with col1:
            with st.expander("Normalized counts of each automation status for selected harm and company", expanded=False):
                st.dataframe(fig16, use_container_width=True)
        #with col2:
            #with st.expander("Number of reported content type normalized for selected harm and company", expanded=False):
                #st.dataframe(fig17, use_container_width=True)
        with col2:
            with st.expander("Analysis of Harm Category vs. Type of Moderation (%) for selected harm and company", expanded=False):
                st.dataframe(fig20, use_container_width=True)
        with col1:
            with st.expander("Analysis of Moderated Content Type vs. Type of Moderation Adopted for selected harm and company", expanded=False):
                st.dataframe(fig21, use_container_width=True)
        with col2:
            with st.expander("Analysis of Moderated Content Type vs. Type of Moderation Adopted normalized for selected harm and company", expanded=False):
                st.dataframe(fig22, use_container_width=True)
        with col1:
            with st.expander("Count of moderation decision per automation status for selected harm and company", expanded=False):
                st.dataframe(fig23, use_container_width=True)
        with col2:
            with st.expander("Number of reported moderation decision for selected harm and company", expanded=False):
                st.dataframe(fig24, use_container_width=True)
    ########################################################################################################
 
    ########################################################################################################
    elif selected_company:
        st.markdown("---")
        st.subheader(f"Analysis for {selected_company}")
        col1, col2 = st.columns(2)

        fig1 = plot_acc_totals_per_company_company(data, selected_company)
        fig2 = plot_acc_totals_per_harm_company(data, selected_company)
        fig3 = plot_acc_totals_per_moderation_action_company(data, selected_company)
        fig4 = plot_acc_totals_per_automation_status_company(data, selected_company)
        fig5 = plot_acc_totals_per_content_type_company(data, selected_company)
        fig6 = plot_acc_totals_company(data, selected_company)
        fig7 = sum_harm1(data, selected_company)
        fig8 = plot_company_dataxxz1(data, selected_company)
        fig9 = plot_company_dataxxz1_normalized(data, selected_company)
        fig10 = plot_content_type_totals1(data, selected_company)
        fig11 = plot_moderation_action_totals1(data, selected_company)
        fig12 = plot_automation_status_totals1(data, selected_company)
        fig13 = plot_harm_totals_per_company1(data, selected_company)
        fig14 = plot_content_type_totals_per_company1(data, selected_company)
        fig15 = plot_automation_status_table_general1(data, selected_company)
        fig16 = plot_normalized_automation_status1(data, selected_company)
        fig17 = plot_harm_content_type_1(data, selected_company)
        fig18 = plot_harm_content_type_normalized1(data, selected_company)
        fig19 = plot_harm_automation_status1(data, selected_company)
        fig20 = plot_harm_automation_status1_normalized(data, selected_company)
        fig21 = plot_content_type_automation_status1(data, selected_company)
        fig22 = plot_content_type_automation_status1_normalized(data, selected_company)
        fig23 = generate_moderation_action_automation_status_figure1(data, selected_company)
        #fig24 = sum_reports_per_moderation_action_per_company1(data, selected_company)


        with col1:
            with st.expander("Analysis of Moderation Actions vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig3, use_container_width=True)
        with col2:
            with st.expander("Analysis of Type of Moderation vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig4, use_container_width=True)
        with col1:
            with st.expander("Analysis of Content Type vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig5, use_container_width=True)
        with col2:
            with st.expander("Analysis of Company vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig1, use_container_width=True)
        with col1:
            with st.expander("Analysis of Harm Category vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig2, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Detection Type (User vs. Automated)", expanded=False):
                st.dataframe(fig6, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Harm Category", expanded=False):
                st.dataframe(fig7, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Type of Moderation", expanded=False):
                st.dataframe(fig12, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Company", expanded=False):
                st.dataframe(fig8, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Company", expanded=False):
                st.dataframe(fig9, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Type of Moderation Action", expanded=False):
                st.dataframe(fig11, use_container_width=True)
        with col2:
            with st.expander(" Analysis of Harm Category vs. Company", expanded=False):
                st.dataframe(fig13, use_container_width=True)
        with col1:
            with st.expander("Analysis of Company vs. Type of Content Moderated", expanded=False):
                st.dataframe(fig14, use_container_width=True)
        with col2:
            with st.expander("Number of Automation Status type per Company", expanded=False):
                st.dataframe(fig15, use_container_width=True)
        with col1:
            with st.expander("Analysis of Company vs. Type of Moderation Adopted", expanded=False):
                st.dataframe(fig16, use_container_width=True)
        with col2:
            with st.expander("Count for each harm per content type", expanded=False):
                st.dataframe(fig17, use_container_width=True)
        with col1:
            with st.expander("Count for each harm per content type Normalized", expanded=False):
                st.dataframe(fig18, use_container_width=True)
        with col2:
            with st.expander("Analysis of Harm Category vs. Type of Moderation", expanded=False):
                st.dataframe(fig19, use_container_width=True)
        with col1:
            with st.expander("Analysis of Harm Category vs. Type of Moderation", expanded=False):
                st.dataframe(fig20, use_container_width=True)
        with col2:
            with st.expander("Analysis of Moderated Content Type vs. Type of Moderation Adopted", expanded=False):
                st.dataframe(fig21, use_container_width=True)
        with col1:
            with st.expander("Analysis of Moderated Content Type vs. Type of Moderation Adopted Normalized", expanded=False):
                st.dataframe(fig22, use_container_width=True)
        with col2:
            with st.expander("Count of moderation decision per automation status", expanded=False):
                st.dataframe(fig23, use_container_width=True)
        #with col1:
          #  with st.expander("Analysis of Company vs. Moderation Actions Adopted", expanded=False):
               # st.dataframe(fig24, use_container_width=True)
    ########################################################################################################

    ########################################################################################################
    elif selected_harm:
        st.markdown("---")
        st.subheader(f"Analysis for {selected_display_harm}")
        col1, col2 = st.columns(2)

        fig1 = plot_acc_totals_per_company_harm(data, selected_harm)
        fig2 = plot_acc_totals_per_harm_harm(data, selected_harm)
        fig3 = plot_acc_totals_per_moderation_action_harm(data, selected_harm)
        fig4 = plot_acc_totals_per_automation_status_harm(data, selected_harm)
        fig5 = plot_acc_totals_per_content_type_harm(data, selected_harm)
        fig6 = plot_acc_totals_harm(data, selected_harm)
        fig7 = sum_harm2(data, selected_harm)
        fig8 = plot_content_type_totals2(data, selected_harm)
        fig9 = plot_moderation_action_totals2(data, selected_harm)
        fig10 = plot_automation_status_totals2(data, selected_harm)
        fig11 = plot_harm_totals_per_company2(data, selected_harm)
        fig12 = plot_automation_status_table_general2(data, selected_harm)
        fig13 = plot_normalized_automation_status2(data, selected_harm)
        fig14 = plot_harm_content_type_normalized2(data, selected_harm)
        fig15 = plot_harm_automation_status2(data, selected_harm)
        fig16 = plot_harm_automation_status2_normalized(data, selected_harm)
        fig17 = plot_content_type_automation_status2(data, selected_harm)
        fig18 = plot_content_type_automation_status2_normalized(data, selected_harm)
        fig19 = generate_moderation_action_automation_status_figure2(data, selected_harm)

        with col1:
            with st.expander("Analysis of Moderation Actions vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig3, use_container_width=True)
        with col2:
            with st.expander("Analysis of Type of Moderation vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig4, use_container_width=True)
        with col1:
            with st.expander("Analysis of Content Type vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig5, use_container_width=True)
        with col2:
            with st.expander("Analysis of Company vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig1, use_container_width=True)
        with col1:
            with st.expander("Analysis of Harm Category vs. Number of Automated or User Flags", expanded=False):
                st.dataframe(fig2, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Detection Type (User vs. Automated)", expanded=False):
                st.dataframe(fig6, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Harm Category", expanded=False):
                st.dataframe(fig7, use_container_width=True)
        with col2:
            with st.expander("Total Moderated Content per Type of Content for harm", expanded=False):
                st.dataframe(fig8, use_container_width=True)
        with col1:
            with st.expander("Total Moderated Content per Type of Moderation for harm", expanded=False):
                st.dataframe(fig9, use_container_width=True)
        with col2:
            with st.expander("Total number of Automation status for harm", expanded=False):
                st.dataframe(fig10, use_container_width=True)
        with col1:
            with st.expander(" Analysis of Harm Category vs. Company for harm", expanded=False):
                st.dataframe(fig11, use_container_width=True)
        with col2:
            with st.expander("Number of Automation Status type per Company for harm", expanded=False):
                st.dataframe(fig12, use_container_width=True)
        with col1:
            with st.expander("Analysis of Company vs. Type of Moderation Adopted for harm", expanded=False):
                st.dataframe(fig13, use_container_width=True)
        with col2:
            with st.expander("Analysis of Harm Category vs. Moderated Content Type for harm", expanded=False):
                st.dataframe(fig14, use_container_width=True)
        with col1:
            with st.expander("Analysis of Harm Category vs. Type of Moderation for harm", expanded=False):
                st.dataframe(fig15, use_container_width=True)
        with col2:
            with st.expander("Analysis of Harm Category vs. Type of Moderation for harm", expanded=False):
                st.dataframe(fig16, use_container_width=True)
        with col1:
            with st.expander("Analysis of Moderated Content Type vs. Type of Moderation Adopted for harm", expanded=False):
                st.dataframe(fig17, use_container_width=True)
        with col2:
            with st.expander("Analysis of Moderated Content Type vs. Type of Moderation Adopted normalized for harm", expanded=False):
                st.dataframe(fig18, use_container_width=True)
        with col1:
            with st.expander("Count of moderation decision per automation status for harm", expanded=False):
                st.dataframe(fig19, use_container_width=True)
    else:
        st.write("Please select one of the options above.")
    ########################################################################################################

########################################################################################################
if __name__ == "__main__":
    main()
########################################################################################################
