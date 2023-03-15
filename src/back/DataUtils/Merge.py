import os

folder_path = "/path/to/folder/"

total_files = len([filename for filename in os.listdir(folder_path) if filename.endswith(".json")])

with open(folder_path + "merged_file.json", "a") as merged_file:
    for index, filename in enumerate(os.listdir(folder_path)):
        if filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), "r") as f:
                lines = f.readlines()

                # Remove the first and last lines from the file
                lines = lines[1:-1]

                # If this is the first file, remove the last line and add a "[" at the beginning
                if index == 0:
                    lines[-1] = lines[-1] + ",\n"
                    lines.insert(0, "[\n")
                # If this is not the first file, remove the first line and add a "," at the end of the last line
                else:
                    lines[-1] = lines[-1][:-1] + ",\n"

                merged_file.writelines(lines)

            percent = (index + 1) / total_files * 100
            print(f"{filename} processed ({percent:.2f}% complete)")

    merged_file.write("]")

print(f"Merged file created at {folder_path}" + "merged_file.json")
