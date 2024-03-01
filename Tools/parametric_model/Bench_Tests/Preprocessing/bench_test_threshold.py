
import pandas as pd
import numpy as np

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('/home/anna/Documents/logs_ulg/flight_log_usb_stick/SysID/Quadrotors/Statistics/good/BENCH_TEST.csv')


std_dev_x = np.std(df['Corr_x'])
std_dev_y = np.std(df['Corr_y'])
std_dev_z = np.std(df['Corr_z'])
# Calculate RMSE for each column
rmse_x = np.sqrt(np.mean((df['Corr_x'] - 0)**2))
rmse_y = np.sqrt(np.mean((df['Corr_y'] - 0)**2))
rmse_z = np.sqrt(np.mean((df['Corr_z'] - 0)**2))


max_error_x = (np.abs(df['Corr_x'])).max()
max_error_y = (np.abs(df['Corr_y'])).max()
max_error_z = (np.abs(df['Corr_z'])).max()

threshold_x = np.mean([max_error_x, rmse_x ])
threshold_y = np.mean([max_error_y, rmse_y ])
threshold_z = np.mean([max_error_z, rmse_z ])

# Print the results
print(f"RMSE for corr_x: {rmse_x}")
print(f"RMSE for corr_y: {rmse_y}")
print(f"RMSE for corr_z: {rmse_z}")


print(f"RMSE for corr_x: {threshold_x}")
print(f"RMSE for corr_y: {threshold_y}")
print(f"RMSE for corr_z: {threshold_z}")