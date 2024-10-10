import os
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

#The base_path is the folder contains the StoneX and other brokers' folder.
base_path = "./20240527_test/20240527"
# The products need to be dealt with
products = ['CHINAA50', 'COPPER', 'EURUSD', 'GBPUSD', 'GER40', 'HK50', 'NAS100', 'SPX500', 'US_OIL', 'US30', 'USDJPY', 'XAGUSD', 'XAUUSD']

## Files Rename
# Considering the name from different brokers are always the same, so every time we get the new data, 
# we can use this part of code to automaticly rename the files.

# Define how to rename
rename_mapping = {
    # CHINAA50
    'CHINA_A50': 'CHINAA50',
    'CHN50': 'CHINAA50',
    'CN50': 'CHINAA50',
    'CHINA50': 'CHINAA50',
    'ChinaA50.p': 'CHINAA50',
    'China50Cash': 'CHINAA50',

    # COPPER
    'Copper': 'COPPER',

    # US_OIL
    'CrudeOIL': 'US_OIL',
    'Crude': 'US_OIL',
    'USOil': 'US_OIL',
    'XTIUSD': 'US_OIL',
    'USOIL.p': 'US_OIL',

    # EURUSD
    'EURUSD': 'EURUSD',
    'EURUSD.p': 'EURUSD',
    'EURUSDmicro': 'EURUSD',

    # GBPUSD
    'GBPUSD': 'GBPUSD',
    'GBPUSD.p': 'GBPUSD',
    'GBPUSDmicro': 'GBPUSD',

    # GER40
    'GERMANY_40': 'GER40',
    'GER30': 'GER40',
    'DE40': 'GER40',
    'DAX.p': 'GER40',
    'GER40Cash': 'GER40',

    # XAUUSD
    'GOLD': 'XAUUSD',
    'GOLD_micro': 'XAUUSD',
    'XAUUSD.p': 'XAUUSD',

    # HK50
    'HK_50': 'HK50',
    'HKG33': 'HK50',
    'HSI.p': 'HK50',
    'HK50Cash': 'HK50',

    # XAGUSD
    'SILVER': 'XAGUSD',
    'SILVER_micro': 'XAGUSD',
    'XAGUSD.p': 'XAGUSD',

    # US30
    'US_30': 'US30',
    'DOW.p': 'US30',
    'US30Cash': 'US30',

    # SPX500
    'US_500': 'SPX500',
    'US500': 'SPX500',
    'SPX500.p': 'SPX500',
    'US500Cash': 'SPX500',

    # NAS100
    'US_TECH100': 'NAS100',
    'USTEC': 'NAS100',
    'NAS100.p': 'NAS100',
    'US100Cash': 'NAS100',

    # USDJPY
    'USDJPY': 'USDJPY',
    'USDJPY.p': 'USDJPY',
    'USDJPYmicro': 'USDJPY',

    # Others
    'USOilSpot': 'USOilSpot',
    'WTI_N4': 'WTI_N4',
    'CHINA300.p': 'CHINA300.p',
    'HGCOP-JUL24': 'HGCOP-JUL24',
    'OIL-JUL24': 'OIL-JUL24',
}

# Rename all the folders
for folder_name in os.listdir(base_path):
    folder_path = os.path.join(base_path, folder_name)
    if os.path.isdir(folder_path): 
        for file_name in os.listdir(folder_path):
            old_file_path = os.path.join(folder_path, file_name)
            new_file_name = rename_mapping.get(file_name, file_name)  
            new_file_path = os.path.join(folder_path, new_file_name)
            
            os.rename(old_file_path, new_file_path)
        print(f"{folder_path} Successfully Renamed")
        
## Deal with the bid and ask's order of magnitude

# Dictionary to store the bid ratios for each product in other brands
bid_ratios = {}

# Function to round the ratio to the nearest 100, 10, 1, 0.1, etc.
def round_ratio(value):
    if value>=500:
        return 1000
    elif value >= 50:
        return 100
    elif value >= 5:
        return 10
    elif value >= 0.5:
        return 1
    elif value >= 0.05:
        return 0.1
    elif value >= 0.005:
        return 0.01
    else:
        return 0.001

# Process StoneX folder first to extract the baseline bid for each product
stonex_folder = os.path.join(base_path, 'StoneX')
stonex_first_bids = {}

# Extract the first bid from StoneX for each product
for product in products:
    product_folder = os.path.join(stonex_folder, product)
    
    if os.path.isdir(product_folder):
        # Loop through each CSV file in the product folder
        for file_name in os.listdir(product_folder):
            if file_name.endswith('.CSV'):
                file_path = os.path.join(product_folder, file_name)
                
                # Read the CSV file into a DataFrame
                df = pd.read_csv(file_path)
                
                # Get the first Bid value
                if 'Bid' in df.columns:
                    stonex_first_bids[product] = df.loc[0, 'Bid']
                    break  # Exit after the first file and first row for each product

# Process other brands and calculate new Bid and Ask based on the ratio
for brand_folder in os.listdir(base_path):
    if brand_folder == 'StoneX':  # Skip StoneX as it has been processed
        continue

    brand_folder_path = os.path.join(base_path, brand_folder)

    # Check if the path is a directory (brand folder)
    if os.path.isdir(brand_folder_path):
        # Process each product folder inside the brand folder
        for product in products:
            product_folder = os.path.join(brand_folder_path, product)

            if os.path.isdir(product_folder):
                # Calculate the ratio for the first file and first row in this product
                for file_name in os.listdir(product_folder):
                    if file_name.endswith('.CSV'):
                        file_path = os.path.join(product_folder, file_name)
                        # Read the CSV file into a DataFrame
                        df = pd.read_csv(file_path)
                        
                        if 'Bid' in df.columns and product in stonex_first_bids:
                            # Get the first Bid value for this brand and product
                            brand_first_bid = df.loc[0, 'Bid']
                            
                            # Calculate the ratio between this brand and StoneX
                            bid_ratio = brand_first_bid / stonex_first_bids[product]
                            # Round the ratio to the nearest 100, 10, 1, 0.1, etc.
                            rounded_ratio = round_ratio(bid_ratio)
                            
                            # Store the rounded ratio for this product in this brand
                            bid_ratios[(brand_folder, product)] = rounded_ratio
                            
                            print(f"Calculated ratio for {brand_folder} - {product}: {rounded_ratio}")
                            break  # Exit after processing the first file for each product

                # Apply the calculated ratio to adjust Bid and Ask for all files in this product
                for file_name in os.listdir(product_folder):
                    if file_name.endswith('.CSV'):
                        file_path = os.path.join(product_folder, file_name)
                        
                        # Read the CSV file into a DataFrame
                        df = pd.read_csv(file_path)
                        
                        if 'Bid' in df.columns and 'Ask' in df.columns:
                            # Get the rounded ratio for this brand and product
                            ratio = bid_ratios.get((brand_folder, product), 1)
                            
                            # Apply the ratio to adjust Bid and Ask
                            df['Bid'] = df['Bid'] / ratio
                            df['Ask'] = df['Ask'] / ratio
                            
                            # Save the updated DataFrame back to the CSV
                            df.to_csv(file_path, index=False)

        # Print a message after processing all files in the brand folder
        print(f"Processed all files in brand folder: {brand_folder}")
print(f"Processed all files")


# =============================================================================
# ## Recaculate new spread and replace old spread
# # Different brands use different rules to caculate the spread. 
# # We can use python code to automaticly caculate all of the spread under the rule of StoneX, 
# # and replace the old spread in the csv files.
# 
# # Dictionary to store the spread ratio for each product in StoneX
# spread_ratios = {}
# 
# # Function to dynamically round small values and avoid 0.00
# def round_decimal_dynamic(value, min_decimal_places=2, max_decimal_places=6):
#     """Rounds the decimal value dynamically, ensuring it's not rounded to zero."""
#     decimal_value = Decimal(value).quantize(Decimal('1.' + '0' * min_decimal_places), rounding=ROUND_HALF_UP)
#     
#     # If the value rounds to 0 with the minimum decimal places, increase precision
#     if decimal_value == Decimal('0.00'):
#         decimal_value = Decimal(value).quantize(Decimal('1.' + '0' * max_decimal_places), rounding=ROUND_HALF_UP)
#     
#     return decimal_value
# 
# # Process StoneX folder first to extract the ratio from the first CSV file and its first row
# stonex_folder = os.path.join(base_path, 'StoneX')
# 
# for product in products:
#     product_folder = os.path.join(stonex_folder, product)
#     
#     if os.path.isdir(product_folder):
#         # Loop through each CSV file in the product folder
#         for file_name in os.listdir(product_folder):
#             if file_name.endswith('.CSV'):
#                 file_path = os.path.join(product_folder, file_name)
#                 
#                 # Read the CSV file into a DataFrame
#                 df = pd.read_csv(file_path)
#                 
#                 # Check if 'Bid', 'Ask', and 'Spread' columns exist
#                 if 'Bid' in df.columns and 'Ask' in df.columns and 'Spread' in df.columns:
#                     df['Spread_Calculated'] = df['Ask'] - df['Bid']
#                     
#                     # Use the first row's ratio of Spread_Calculated to Spread
#                     first_ratio = df.loc[0, 'Spread'] / df.loc[0, 'Spread_Calculated']
#                     
#                     # Use the round_decimal_dynamic function to round the ratio, avoiding 0.00
#                     rounded_ratio = round_decimal_dynamic(first_ratio)
#                     
#                     # Store this rounded ratio for the product
#                     spread_ratios[product] = rounded_ratio
#                     print(f"First ratio for {product} in StoneX (rounded): {rounded_ratio}")
#                     break  # Exit after the first file and first row
#                 else:
#                     print(f"File {file_name} in {product} does not contain required columns.")
#                 break  # Stop after processing the first file for each product
# 
# # Apply the extracted ratio to other brand folders
# for brand_folder in os.listdir(base_path):
#     if brand_folder == 'StoneX':  # Skip StoneX as it has been processed
#         continue
# 
#     brand_folder_path = os.path.join(base_path, brand_folder)
# 
#     # Check if the path is a directory (brand folder)
#     if os.path.isdir(brand_folder_path):
#         # Process each product folder inside the brand folder
#         for product in products:
#             product_folder = os.path.join(brand_folder_path, product)
# 
#             if os.path.isdir(product_folder):
#                 # Loop through each CSV file in the product folder
#                 for file_name in os.listdir(product_folder):
#                     if file_name.endswith('.CSV'):
#                         file_path = os.path.join(product_folder, file_name)
#                         
#                         # Read the CSV file into a DataFrame
#                         df = pd.read_csv(file_path)
#                         
#                         # Check if 'Bid', 'Ask', and 'Spread' columns exist
#                         if 'Bid' in df.columns and 'Ask' in df.columns and 'Spread' in df.columns:
#                             # Use the ratio from StoneX to calculate new Spread_Calculated
#                             if product in spread_ratios:
#                                 df['Spread'] = (df['Ask'] - df['Bid']) * float(spread_ratios[product])
#                         else:
#                             print(f"File {file_name} in {product} does not contain required columns.")
#                         
#                         # Overwrite the original CSV file with the updated DataFrame
#                         df.to_csv(file_path, index=False)
# 
#         # Print a message after processing all files in the brand folder
#         print(f"Processed all files in brand folder: {brand_folder}")
# print(f"Processed all files")
# =============================================================================


# Apply the extracted ratio to other brand folders
for brand_folder in os.listdir(base_path):

    brand_folder_path = os.path.join(base_path, brand_folder)

    # Check if the path is a directory (brand folder)
    if os.path.isdir(brand_folder_path):
        # Process each product folder inside the brand folder
        for product in products:
            product_folder = os.path.join(brand_folder_path, product)

            if os.path.isdir(product_folder):
                # Loop through each CSV file in the product folder
                for file_name in os.listdir(product_folder):
                    if file_name.endswith('.CSV'):
                        file_path = os.path.join(product_folder, file_name)
                        
                        # Read the CSV file into a DataFrame
                        df = pd.read_csv(file_path)
                        
                        # Check if 'Bid', 'Ask', and 'Spread' columns exist
                        if 'Bid' in df.columns and 'Ask' in df.columns and 'Spread' in df.columns:
                            # Use the ratio from StoneX to calculate new Spread_Calculated
                                df['Spread'] = (df['Ask'] - df['Bid'])
                        else:
                            print(f"File {file_name} in {product} does not contain required columns.")
                        
                        # Overwrite the original CSV file with the updated DataFrame
                        df.to_csv(file_path, index=False)

        # Print a message after processing all files in the brand folder
        print(f"Processed all files in brand folder: {brand_folder}")
print(f"Processed all files")


## Get Dataframe

#Function to extract date from file name (format: MMDDYYYY)
def extract_date_from_filename(filename):
    date_str = filename.split('.')[0]  # Extract '05192024' from '05192024.CSV'
    return pd.to_datetime(date_str, format='%m%d%Y')

# Function to convert the 'Time' column into proper datetime format, including five-digit milliseconds
def parse_time_with_five_milliseconds(time_str):
    try:
        # Split into time and millisecond parts
        time_parts = time_str.split(' ')
        time = time_parts[0]  # e.g. '20:39:27'
        milliseconds = time_parts[1] if len(time_parts) > 1 else '00000'  # Handle missing milliseconds
        
        # Normalize the milliseconds to always be 5 digits
        milliseconds = milliseconds.ljust(5, '0')[:5]  # Pad or truncate to 5 digits

        # Combine time and milliseconds into a full time with milliseconds
        full_time = f"{time}.{milliseconds}"
        return full_time
    except Exception as e:
        print(f"Error parsing time string: {time_str} - {e}")
        return time_str  # Return original in case of error
    
# Get StoneX file

stonex_data = {}
brand_folder = 'StoneX'  
brand_folder_path = os.path.join(base_path, brand_folder)

for product in products:
    product_folder = os.path.join(brand_folder_path, product)
    
    if os.path.isdir(product_folder):
        # Loop through each CSV file in the product folder
        for file_name in os.listdir(product_folder):
            if file_name.endswith('.CSV'):
                file_path = os.path.join(product_folder, file_name)
                
                # Extract date from the file name
                file_date = extract_date_from_filename(file_name)

                # Read the CSV file into a DataFrame
                df = pd.read_csv(file_path)

                # Ensure necessary columns exist
                if 'Time' in df.columns and 'Bid' in df.columns and 'Ask' in df.columns:
                    # Convert 'Time' column with five-digit milliseconds
                    df['Time'] = df['Time'].apply(parse_time_with_five_milliseconds)

                    # Combine the extracted date with the 'Time' column to create 'Timestamp'
                    df['Timestamp'] = pd.to_datetime(file_date.strftime('%Y-%m-%d') + ' ' + df['Time'], format='%Y-%m-%d %H:%M:%S.%f')
                    df = df[['Timestamp', 'Bid', 'Ask', 'Spread']]
                                        
                    # Group by hour for StoneX and calculate hourly average
                    hourly_avg = df.resample('h', on='Timestamp').mean().reset_index()

                    # Calculate the count of records in each hour
                    hourly_count = df.resample('h', on='Timestamp').size().reset_index(name='DataCount')

                    # Merge the mean and count DataFrames
                    hourly_avg = pd.merge(hourly_avg, hourly_count, on='Timestamp')
                    hourly_avg['Product'] = product
                    hourly_avg['Brand'] = brand_folder
                    #print(hourly_avg)
                    
                    # Store the results in stonex_data            
                    if product not in stonex_data:
                        stonex_data[product] = pd.DataFrame()  # Initialize if not exist
                    
                    # Append the data to stonex_data
                    stonex_data[product] = pd.concat([stonex_data[product], hourly_avg], ignore_index=True)

# Combine all product data into a single DataFrame
all_data = pd.concat(stonex_data.values(), ignore_index=True)
all_data['Spread_StoneX']=all_data['Spread']
all_data['Spread_Diff']=0

# Save the combined DataFrame to a CSV file
# output_csv_path = os.path.join(base_path, 'stonex_data_combined.csv')
# all_data.to_csv(output_csv_path, index=False)

# print(f"Data has been saved to {output_csv_path}")

# Get other file

# Initialize an empty dictionary to store data for each brand
other_brands_data = {}

# Read the StoneX data into a DataFrame
stonex_combined_data = pd.concat(stonex_data.values(), ignore_index=True)

# Loop through all brands in the base_path directory
for brand_folder in os.listdir(base_path):
    brand_folder_path = os.path.join(base_path, brand_folder)
    
    # Skip the 'StoneX' brand (since its data has already been processed)
    if brand_folder == 'StoneX':
        continue

    # Check if the current brand folder is a directory
    if os.path.isdir(brand_folder_path):
        
        for product in products:
            product_folder = os.path.join(brand_folder_path, product)
            
            if os.path.isdir(product_folder):
                # Loop through each CSV file in the product folder
                for file_name in os.listdir(product_folder):
                    if file_name.endswith('.CSV'):
                        file_path = os.path.join(product_folder, file_name)
                        
                        # Extract date from the file name
                        file_date = extract_date_from_filename(file_name)

                        # Read the CSV file into a DataFrame
                        df = pd.read_csv(file_path)

                        # Ensure necessary columns exist
                        if 'Time' in df.columns and 'Bid' in df.columns and 'Ask' in df.columns:
                            # Convert 'Time' column with five-digit milliseconds
                            df['Time'] = df['Time'].apply(parse_time_with_five_milliseconds)

                            # Combine the extracted date with the 'Time' column to create 'Timestamp'
                            df['Timestamp'] = pd.to_datetime(file_date.strftime('%Y-%m-%d') + ' ' + df['Time'], format='%Y-%m-%d %H:%M:%S.%f')
                            df = df[['Timestamp', 'Bid', 'Ask', 'Spread']]
                                                
                            # Group by hour and calculate hourly average
                            hourly_avg = df.resample('h', on='Timestamp').mean().reset_index()

                            # Calculate the count of records in each hour
                            hourly_count = df.resample('h', on='Timestamp').size().reset_index(name='DataCount')

                            # Merge the mean and count DataFrames
                            hourly_avg = pd.merge(hourly_avg, hourly_count, on='Timestamp')
                            hourly_avg['Product'] = product
                            hourly_avg['Brand'] = brand_folder
                            
                            # Store the results in other_brands_data            
                            if brand_folder not in other_brands_data:
                                other_brands_data[brand_folder] = pd.DataFrame()  # Initialize if not exist
                            
                            # Append the data to other_brands_data
                            other_brands_data[brand_folder] = pd.concat([other_brands_data[brand_folder], hourly_avg], ignore_index=True)

# Combine all other brand data into a single DataFrame
all_other_brands_data = pd.concat(other_brands_data.values(), ignore_index=True)

# Merge the StoneX data with the other brands data on 'Timestamp' and 'Product' to calculate Spread_Diff
combined_data_with_diff = pd.merge(all_other_brands_data, stonex_combined_data[['Timestamp', 'Product', 'Spread']], on=['Timestamp', 'Product'], how='left', suffixes=('', '_StoneX'))

# Calculate Spread_Diff as the difference between the other brand's Spread and StoneX's Spread for the same product
combined_data_with_diff['Spread_Diff'] = combined_data_with_diff['Spread'] - combined_data_with_diff['Spread_StoneX']

# Save the combined DataFrame with Spread_Diff to a CSV file
# output_csv_path = os.path.join(base_path, 'other_brands_data_with_spread_diff.csv')
# combined_data_with_diff.to_csv(output_csv_path, index=False)

# print(f"Other brands data with Spread_Diff has been saved to {output_csv_path}")


# To CSV
stonex_df =all_data
other_brands_df = combined_data_with_diff

# Combine the two DataFrames
combined_df = pd.concat([stonex_df, other_brands_df], ignore_index=True)

# Drop rows where DataCount is less than 5
filtered_combined_df = combined_df[combined_df['DataCount'] >= 5]

# Define the output path for the final combined CSV
output_combined_file = os.path.join(base_path, 'Hour_level_data.csv')

# Save the filtered combined data to a new CSV file
filtered_combined_df.to_csv(output_combined_file, index=False)

print(f"Final combined and filtered CSV file saved at {output_combined_file}")








