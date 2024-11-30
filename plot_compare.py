import glob
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

# Create an output directory if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

# Initialize an empty DataFrame to collect all data
all_data = pd.DataFrame()

# Get all .rta.csv files
files = glob.glob('*.rta.csv')

for file in files:
    filename = os.path.basename(file)
    # Updated regex for new filename format
    match = re.match(r'([A-Za-z]+)_(\d+)_([A-Za-z]+)_jobs\.rta\.csv', filename)
    if match:
        type_name = match.group(1)       # Extract TYPE (e.g., CPU)
        iteration = int(match.group(2)) # Extract ITERATION (e.g., 0, 1, 2)
        method = match.group(3).upper() # Extract METHOD (e.g., NEW, NAIVE)
    else:
        print(f"Filename {filename} does not match expected pattern.")
        continue

    # Read the CSV file
    try:
        df = pd.read_csv(file)
    except Exception as e:
        print(f"Error reading {file}: {e}")
        continue

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Add 'type', 'iteration', and 'method' columns
    df['type'] = type_name
    df['iteration'] = iteration
    df['method'] = method

    # Append to the all_data DataFrame
    all_data = pd.concat([all_data, df], ignore_index=True)

# Ensure that the necessary columns are present
expected_columns = ['type', 'iteration', 'task id', 'job id', 'bcct', 'wcct', 'bcrt', 'wcrt', 'method']
all_data.columns = all_data.columns.str.strip().str.lower()

missing_columns = set(expected_columns) - set(all_data.columns)
if missing_columns:
    print(f"Missing columns in data: {missing_columns}")
    exit()

# Convert columns to appropriate data types
all_data['iteration'] = all_data['iteration'].astype(int)
all_data['task id'] = all_data['task id'].astype(int)
all_data['job id'] = all_data['job id'].astype(int)

# Create directories for output
types = all_data['type'].unique()
for type_name in types:
    type_dir = os.path.join('output', type_name)
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)

    # Filter data for the current type
    type_data = all_data[all_data['type'] == type_name]

    # Get all Task IDs
    task_ids = type_data['task id'].unique()

    for task_id in task_ids:
        task_data = type_data[type_data['task id'] == task_id]

        # List of values to plot
        values = ['bcrt', 'wcrt', 'bcct', 'wcct']
        for value_name in values:
            plt.figure()

            # Separate data for NAIVE and NEW
            naive_data = task_data[task_data['method'] == 'NAIVE']
            new_data = task_data[task_data['method'] == 'NEW']

            # Plot NAIVE data
            for job_id in naive_data['job id'].unique():
                job_data = naive_data[naive_data['job id'] == job_id].sort_values('iteration')
                plt.plot(job_data['iteration'], job_data[value_name], marker='P', linestyle='-', label=f'NAIVE - Job {job_id}')

            # Plot NEW data
            for job_id in new_data['job id'].unique():
                job_data = new_data[new_data['job id'] == job_id].sort_values('iteration')
                plt.plot(job_data['iteration'], job_data[value_name], marker='x', linestyle='--', label=f'NEW - Job {job_id}')

            # Chart customization
            plt.title(f'{type_name} Task {task_id} {value_name.upper()} Comparison')
            plt.xlabel('Iteration')
            plt.ylabel(value_name.upper())
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            # Save plot
            plot_filename = f'{type_name}_Task{task_id}_{value_name.upper()}_Comparison.png'
            plt.savefig(os.path.join(type_dir, plot_filename))
            plt.close()

