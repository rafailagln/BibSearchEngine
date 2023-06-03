import os
import json
import gzip
import threading
import time

from distributed.utils import send_request

doc_id_lock = threading.Lock()
load_lock = threading.Lock()


# TODO: Check all blocking parts (see example load_to_nodes with new thread)
def get_shard(doc_id, num_shards):
    """
    Returns the shard ID based on the document ID and number of shards.

    Inputs:
    - doc_id: The document ID.
    - num_shards: The number of shards.

    Output:
    - The shard ID.
    """
    shard_id = doc_id % num_shards
    return shard_id + 1


class FastJsonLoader:
    def __init__(self, folder_path, documents_per_file, node_id, node_count):
        """
        Initializes the FastJsonLoader instance.

        Inputs:
        - folder_path: The path to the folder containing the JSON files.
        - documents_per_file: The number of documents to store in each file.
        - node_id: The ID of the node.
        - node_count: The total number of nodes.

        Output: None
        """
        self.folder_path = folder_path
        self.documents = {}
        self.metadata = {}
        self.doc_id = node_id
        self.id_file = f'{folder_path}/doc_ids.json'
        self.documents_per_file = documents_per_file
        self.ids_exist = False
        # self.node_id = node_id
        self.node_count = node_count

    def load_ids(self):
        """
        Loads the document IDs from the doc_file.

        Input: None

        Output: None
        """
        if self.id_file_exists():
            with open(self.id_file, 'r') as f:
                # Convert keys to integers
                self.metadata = {int(k): v for k, v in json.load(f).items()}
            self.ids_exist = True
        else:
            self.metadata = {}

    def save_ids(self):
        """
        Saves the document IDs to the doc_file.

        Input: None

        Output: None
        """
        with open(self.id_file, 'w') as f:
            json.dump(self.metadata, f)

    def load_documents(self):
        """
        Loads the documents from the JSON files in the specified folder.
        This method reads the JSON files in the folder and extracts the relevant document information,
        such as title, abstract, URL, and referenced-by count. It organizes the documents into separate
        compressed data files based on a specified number of documents per file. The method also handles
        metadata about the document files.

        Input: None

        Output: None
        """
        self.load_ids()
        counter = 1
        file_count = 1
        total_files = len([f for f in os.listdir(self.folder_path) if f.endswith(".gz")])

        skip_metadata = True
        if len(self.metadata) == 0:
            skip_metadata = False

        for file in os.listdir(self.folder_path):
            skip_file = False
            if file.endswith('.gz'):
                file_path = os.path.join(self.folder_path, file)
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    json_data = json.load(f)
                file_content = []
                document_counter = 0

                for item in json_data['items']:
                    title_field = item.get('title', '')
                    title = title_field[0].replace('\n', ' ') if isinstance(title_field, list) else title_field.replace(
                        '\n', ' ')
                    abstract = item.get('abstract', '').replace('\n', ' ')
                    url = item.get('URL', '').replace('\n', ' ')
                    referenced_by = item.get('is-referenced-by-count', 0)

                    if not skip_metadata:
                        file_content.append({
                            'doc_id': self.doc_id,
                            'title': title,
                            'abstract': abstract,
                            'URL': url,
                            'referenced_by': referenced_by
                        })
                    else:
                        if self.doc_id in self.metadata and self.metadata[self.doc_id]['in_fl'] == file:
                            file_content.append({
                                'doc_id': self.doc_id,
                                'title': title,
                                'abstract': abstract,
                                'URL': url,
                                'referenced_by': referenced_by
                            })
                        else:
                            print(f'File {file} contents might have changed. Skipping '
                                  f'file. Delete doc_ids.json to rebuild the metadata')
                            skip_file = True
                            break

                    if not skip_metadata:
                        self.metadata[self.doc_id] = {
                            'private_index': len(file_content) - 1,
                            'file': f'documents_{file_count}.gz',
                            'in_fl': file
                        }

                    # self.doc_id += self.node_count
                    self.doc_id += self.node_count
                    document_counter += 1

                    if document_counter == self.documents_per_file:
                        compressed_data = gzip.compress(json.dumps(file_content).encode('utf-8'))
                        self.documents[f'documents_{file_count}.gz'] = compressed_data
                        file_count += 1
                        file_content = []
                        document_counter = 0

                if skip_file:
                    continue

                if file_content:
                    compressed_data = gzip.compress(json.dumps(file_content).encode('utf-8'))
                    self.documents[f'documents_{file_count}.gz'] = compressed_data
                    file_count += 1

                # print(f'Loaded document {file} in memory ({counter / total_files * 100:.2f}%)', end="\r", flush=True)
                print(f'Loaded document {file} in memory ({counter / total_files * 100:.2f}%)')
                counter += 1

        if not self.ids_exist:
            self.save_ids()

    def find_highest_numbered_file(self):
        """
        Finds the file with the highest number in the file name.

        Input: None

        Output: The file name with the highest number.
        """
        highest_number = None
        highest_numbered_file = None

        for file_name in os.listdir(self.folder_path[:-5] + "save/"):
            if file_name.endswith('.json.gz') and file_name.startswith('documents_'):
                # Extract the number from the file name
                try:
                    number = int(file_name.split('_')[1].split('.')[0])
                except ValueError:
                    # Skip files that don't have a valid number
                    continue

                # Check if the current number is higher than the current highest number
                if highest_number is None or number > highest_number:
                    highest_number = number
                    highest_numbered_file = file_name

        return highest_numbered_file

    def insert_documents(self, new_documents):
        """
        Inserts new documents into the JSON files.

        Input:
        - new_documents: A list of new documents to insert.

        Output: None
        """
        custom_file_prefix = 'documents_'
        last_file = self.find_highest_numbered_file()
        if last_file is None:
            last_file = f"{custom_file_prefix}1.json.gz"

        last_document_data = json.loads(gzip.decompress(self.documents.get(last_file, b'')).decode('utf-8') or "[]")
        remaining_slots = self.documents_per_file - len(last_document_data)

        for new_doc in new_documents:
            if remaining_slots > 0 and len(last_document_data) != 0:
                last_document_data.append(new_doc)
                index = len(last_document_data) - 1
                self.metadata[new_doc.get('doc_id')] = {'index': index, 'file': last_file}
                remaining_slots -= 1
            else:
                self.save_new_data(last_document_data, last_file)
                if len(last_document_data) == 0:
                    new_file_number = int(last_file.split(custom_file_prefix)[-1].split(".")[0])
                else:
                    new_file_number = int(last_file.split(custom_file_prefix)[-1].split(".")[0]) + 1
                last_file = f'{custom_file_prefix}{new_file_number}.json.gz'
                last_document_data = [new_doc]
                index = 0
                self.metadata[new_doc.get('doc_id')] = {'index': index, 'file': last_file}
                remaining_slots = self.documents_per_file - 1

        self.save_new_data(last_document_data, last_file)
        self.save_ids()

    def save_new_data(self, last_document_data, last_file):
        """
        Saves the new data to a JSON file.

        Input:
        - last_document_data: The data to be saved.
        - last_file: The file name to save the data to.

        Output: None
        """
        if len(last_document_data) != 0:
            file_path = os.path.join(self.folder_path[:-5] + "save/", last_file)
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                json.dump({"items": last_document_data}, f)

            compressed_data = gzip.compress(json.dumps(last_document_data).encode('utf-8'))
            self.documents[last_file] = compressed_data

    def get_data(self, doc_ids, sort_by_doc_id=False):
        """
        Retrieves data for the given document IDs.

        Inputs:
        - doc_ids (list): A list of document IDs to retrieve data for.
        - sort_by_doc_id (bool): Indicates whether to sort the results by doc_id. If set to True,
          the results will be sorted based on the order of the provided doc_ids.

        Outputs:
        - A list of dictionaries containing the retrieved data. Each dictionary represents a document
          and contains the following fields:
            - 'order' (int): The order of the document ID in the input list (only present if sort_by_doc_id is True).
            - 'doc_id' (int): The ID of the document.
            - 'title' (str): The title of the document.
            - 'abstract' (str): The abstract of the document.
            - 'URL' (str): The URL of the document.
            - 'referenced_by' (int): The number of times the document is referenced by other documents.
        """
        file_buckets = {}
        doc_id_order = {doc_id: i for i, doc_id in enumerate(doc_ids)}

        # Create buckets for doc_ids belonging to the same file
        for doc_id in doc_ids:
            if doc_id in self.metadata:
                file = self.metadata[doc_id]['file']
                if file not in file_buckets:
                    file_buckets[file] = []
                file_buckets[file].append(doc_id)

        # Retrieve titles, abstracts, and URLs for each bucket
        unordered_results = []
        for file, bucket_doc_ids in file_buckets.items():
            compressed_data = self.documents[file]
            item_data = json.loads(gzip.decompress(compressed_data).decode('utf-8'))

            for doc_id in bucket_doc_ids:
                index = self.metadata[doc_id]['private_index']
                item = item_data[index]
                unordered_results.append({
                    "order": doc_id_order[doc_id],
                    "doc_id": doc_id,
                    "title": item['title'],
                    "abstract": item['abstract'],
                    "URL": item['URL'],
                    "referenced_by": item['referenced_by']
                })

        # Sort results based on the order of doc_ids in the input or based on doc_ids
        if sort_by_doc_id:
            return sorted(unordered_results, key=lambda x: x['order'])
        else:
            return unordered_results

    def delete_documents(self, doc_ids_to_delete):
        """
        Deletes documents from the JSON files.

        Input:
        - doc_ids_to_delete: A list of document IDs to delete.

        Output: None
        """
        # Group doc_ids by the file they belong to
        file_buckets = {}
        for doc_id in doc_ids_to_delete:
            if doc_id in self.metadata:
                file = self.metadata[doc_id]['file']
                if file not in file_buckets:
                    file_buckets[file] = []
                file_buckets[file].append(doc_id)

        # Remove documents from each file and rewrite the file
        for file, bucket_doc_ids in file_buckets.items():
            compressed_data = self.documents[file]
            item_data = json.loads(gzip.decompress(compressed_data).decode('utf-8'))

            new_item_data = [item for item in item_data if item['doc_id'] not in bucket_doc_ids]

            # Rewrite the file on disk
            self.save_new_data(new_item_data, file)

            # Update metadata
            for doc_id in bucket_doc_ids:
                del self.metadata[doc_id]

        self.save_ids()

    def count_documents_in_folder(self):
        """
        Counts the total number of documents in the folder.

        Input:
        - folder_path: The path to the folder containing the JSON files.

        Output:
        - The number of documents.
        """
        total_documents = 0

        # Loop through all files in the folder
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".json.gz"):
                file_path = os.path.join(self.folder_path, file_name)
                with gzip.open(file_path, 'rt') as gz_file:
                    json_content = gz_file.read()
                    json_docs = json.loads(json_content)
                    total_documents += len(json_docs['items'])

        return total_documents

    def get_all_documents(self):
        """
        Retrieves all documents from the JSON files.

        Input:
        - folder_path: The path to the folder containing the JSON files.

        Output:
        - A list of dictionaries containing all the documents.
        """
        all_ids = []
        for i in range(1, self.doc_id):
            all_ids.append(i)
        return self.get_data(all_ids)

    def id_file_exists(self):
        """
        Checks if the ID file exists in the given folder.

        Input:
        - folder_path: The path to the folder.

        Output:
        - True if the ID file exists, False otherwise.
        """
        if os.path.exists(self.id_file):
            return True
        else:
            return False
