import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets


class CleanData:
    @staticmethod
    def process_data(input_csv, relevant_states, prefix, drop_list):
        # Load the data
        original_data = pd.read_csv(input_csv)
        
              

        # Make a copy of the original data
        data = original_data.copy()

        # Drop specified columns
        data.drop(drop_list, axis=1, inplace=True)
        
       

        # Creating a year variable with the specified prefix
        col_dict = {str(i): f'{prefix}{i}' for i in range(1969, 2003+1)}
        data.rename(columns=col_dict, inplace=True)
        
       

        # Selecting the relevant states
        data_r = data[data['AreaName'].apply(lambda x: x in relevant_states)]

        # Reset indexing
        data_r.reset_index(inplace=True, drop=True)

        # Transforming wide to long format
        data_long = pd.wide_to_long(data_r, stubnames=prefix, i='AreaName', j='year')

      

        return data_long
    
    @staticmethod
    def process_employment_data(input_csv, relevant_states):
        # Load the data with a different encoding and specify dtype to avoid mixed type warning
        dtype = {col: 'str' for col in range(2, 62)}
        emp_original = pd.read_csv(input_csv, encoding='latin1', dtype=dtype)
        
       

        # Make a copy of the original data
        emp = emp_original.copy()

        # Filter the variables of interest
        I = emp.Description.str.contains('Total employment')
        I |= emp.Description.str.contains('Less: Contributions for government social insurance 5/')
        emp_rel = emp.loc[I == True].copy()  # use .copy() to avoid SettingWithCopyWarning

       

        # Drop irrelevant columns
        drop_list = ["GeoFIPS", "Region", "TableName", "LineCode", "IndustryClassification", "Unit"]
        emp_rel.drop(drop_list, axis=1, inplace=True)

        # Reset indexing
        emp_rel.reset_index(inplace=True, drop=True)

        # Selecting the relevant states
        emp_r = emp_rel[emp_rel['GeoName'].apply(lambda x: x in relevant_states)].copy()  # use .copy() to avoid SettingWithCopyWarning

        # Create a dictionary to map the current descriptions to new ones
        desc_dict = {
            'Total employment ': 'emp',
            'Less: Contributions for government social insurance 5/': 'soc_gov'
        }

        # Replace the names in the DataFrame
        emp_r.loc[:, 'Description'] = emp_r['Description'].replace(desc_dict)

        # Melt the DataFrame to make it longer
        emp_r_melted = emp_r.melt(id_vars=['GeoName', 'Description'], var_name='Year', value_name='Value')

        # Pivot the melted DataFrame to make it wider
        emp_r_pivot = emp_r_melted.pivot_table(index=['Year', 'GeoName'], columns='Description', values='Value', aggfunc='sum')

        # Reset the index to make 'Year' and 'GeoName' regular columns again
        emp_r_pivot.reset_index(inplace=True)
        emp_r_pivot.columns.name = None

       

        return emp_r_pivot

if __name__ == "__main__":
    relevant_states = ["Alabama", "Arkansas", "Florida", "California", "Idaho", "Indiana", "Minnesota", "Kentucky", "Wyoming", "Missouri", "Nevada", "New Mexico", "North Dakota", "Oregon", "Pennsylvania", "Utah"]
    
    # Process the disposable income data
    input_csv_di = "spi0404-5.csv"
    drop_list_di = ["Per capita disposable personal income 2/", "State Code", "Region Code"]
    di_long = CleanData.process_data(input_csv_di, relevant_states, prefix="di", drop_list=drop_list_di)
    
    # Process the population data
    input_csv_pop = "spi0404-3.csv"
    drop_list_pop = ["Population 1/", "State Code", "Region Code"]
    pop_long = CleanData.process_data(input_csv_pop, relevant_states, prefix="pop", drop_list=drop_list_pop)
    
    # Process the employment data
    input_csv_emp = "CAINC4__ALL_AREAS_1969_2022.csv"
    emp_pivot = CleanData.process_employment_data(input_csv_emp, relevant_states)
