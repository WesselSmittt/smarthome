import os

data_files =  ["access_log.json", "user_info.json"]

for filename in data_files:
    file_path = os.path.abspath(filename)
    print(f"File: {filename}")
    print(f"Path: {file_path}")
    print("-" * 50)