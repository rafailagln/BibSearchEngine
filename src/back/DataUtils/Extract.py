import os
import gzip
import concurrent.futures

folder_path = "/path/to/folder/"

processed_files = 0
total_files = len([filename for filename in os.listdir(folder_path) if filename.endswith(".json.gz")])


def process_file(filename):
    output_filename = filename[:-3]

    with gzip.open(os.path.join(folder_path, filename), "rb") as gz_file, open(
            os.path.join(folder_path, output_filename), "wb") as output_file:
        content = gz_file.read()
        output_file.write(content)

    global processed_files
    processed_files += 1
    percent_complete = (processed_files / total_files) * 100
    print(f"Processed {processed_files} of {total_files} files ({percent_complete:.2f}% complete)")


def main():
    files = [filename for filename in os.listdir(folder_path) if filename.endswith(".json.gz")]

    num_threads = os.cpu_count()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_file, filename) for filename in files]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    print("Done!")


if __name__ == '__main__':
    main()
