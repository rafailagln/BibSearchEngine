import os
import concurrent.futures

folder_path = "/path/to/folder/"
total_files = len([filename for filename in os.listdir(folder_path) if filename.endswith(".json")])


def process_file(index, filename):
    # rw
    with open(os.path.join(folder_path, filename), "r+") as f:
        lines = f.readlines()

        # Remove the first two lines and the last line
        lines = lines[2:-1]

        lines.insert(0, "[\n")

        # Move the file pointer to the beginning of the file and truncate it
        f.seek(0)
        f.truncate()

        f.writelines(lines)

    percent = (index + 1) / total_files * 100
    print(f"{filename} processed ({percent:.2f}% complete)")


with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    futures = [executor.submit(process_file, index, filename) for index, filename in enumerate(os.listdir(folder_path))
               if filename.endswith(".json")]

    # join
    for future in concurrent.futures.as_completed(futures):
        pass

print("Done!")
