import sys


def update_load_folder_path(_file_path, new_value):
    _file_path += "/config.ini"
    # Read the file
    with open(_file_path, 'r') as file:
        lines = file.readlines()

    # Find the line with the property 'load_folder_path'
    for i, line in enumerate(lines):
        if line.startswith('load_folder_path'):
            # Update the value
            lines[i] = f'load_folder_path = {new_value}\n'
            break

    # Save the modified file
    with open(_file_path, 'w') as file:
        file.writelines(lines)


# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print('Usage: python script.py <file_path> <new_load_folder_path>')
else:
    file_path = sys.argv[1]
    new_load_folder_path = sys.argv[2]
    update_load_folder_path(file_path, new_load_folder_path)
