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
    # Extract type and iteration from the filename using regex
    # Expected filename format: TYPE_ITERATION_*.rta.csv
    match = re.match(r'([A-Za-z]+)_(\d+)_.*\.rta\.csv', filename)
    if match:
        type_name = match.group(1)
        iteration = int(match.group(2))
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

    # Add 'type' and 'iteration' columns
    df['type'] = type_name
    df['iteration'] = iteration

    # Append to the all_data DataFrame
    all_data = pd.concat([all_data, df], ignore_index=True)

# Ensure that the necessary columns are present
expected_columns = ['type', 'iteration', 'task id', 'job id', 'bcct', 'wcct', 'bcrt', 'wcrt']
all_data.columns = all_data.columns.str.strip().str.lower()

missing_columns = set(expected_columns) - set(all_data.columns)
if missing_columns:
    print(f"Missing columns in data: {missing_columns}")
    exit()

# Convert columns to appropriate data types
all_data['iteration'] = all_data['iteration'].astype(int)
all_data['task id'] = all_data['task id'].astype(int)
all_data['job id'] = all_data['job id'].astype(int)

# Create a directory for each type
types = all_data['type'].unique()
for type_name in types:
    type_dir = os.path.join('output', type_name)
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)

    type_data = all_data[all_data['type'] == type_name]

    # Get all Task IDs
    task_ids = type_data['task id'].unique()

    for task_id in task_ids:
        task_data = type_data[type_data['task id'] == task_id]

        # List of values to plot
        values = ['bcrt', 'wcrt', 'bcct', 'wcct']
        for value_name in values:
            plt.figure()

            # Get all Job IDs
            job_ids = task_data['job id'].unique()

            for job_id in job_ids:
                job_data = task_data[task_data['job id'] == job_id]

                # Sort by iteration to ensure the lines are connected properly
                job_data = job_data.sort_values('iteration')

                # Plot the data
                plt.plot(job_data['iteration'], job_data[value_name], marker='o', label=f'Job {job_id}')

                # Annotate each data point with its value
                for x, y in zip(job_data['iteration'], job_data[value_name]):
                    plt.annotate(f'{y}', xy=(x, y), textcoords='offset points', xytext=(0, 5), ha='center', fontsize=8)

            plt.title(f'{type_name} Task {task_id} {value_name.upper()} over Iterations')
            plt.xlabel('Iteration')
            plt.ylabel(value_name.upper())
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plot_filename = f'{type_name}_Task{task_id}_{value_name.upper()}.png'
            plt.savefig(os.path.join(type_dir, plot_filename))
            plt.close()
