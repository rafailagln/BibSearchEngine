import os
import json
import gzip
import configparser


def read_config_file(config_file_path):
    config = configparser.ConfigParser()
    config.read(config_file_path)
    try:
        documents_per_file = int(config.get('Settings', 'documents_per_file'))
    except (configparser.NoSectionError, configparser.NoOptionError):
        documents_per_file = 100  # Default value if the setting is not found
    return documents_per_file


class FastJsonLoader:
    def __init__(self, folder_path, documents_per_file):
        self.folder_path = folder_path
        self.documents = {}
        self.metadata = {}
        self.doc_id = 1
        self.id_file = 'doc_ids.json'
        self.documents_per_file = documents_per_file
        self.load_ids()
        self.ids_exist = False

    def load_ids(self):
        if os.path.exists(self.id_file):
            with open(self.id_file, 'r') as f:
                self.metadata = json.load(f)
            self.ids_exist = True
        else:
            self.metadata = {}

    def save_ids(self):
        with open(self.id_file, 'w') as f:
            json.dump(self.metadata, f)

    def load_documents(self):
        counter = 1
        file_count = 1
        total_files = len([f for f in os.listdir(self.folder_path) if f.endswith(".gz")])
        for file in os.listdir(self.folder_path):
            if file.endswith('.gz'):
                file_path = os.path.join(self.folder_path, file)
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    json_data = json.load(f)
                file_content = []
                document_counter = 0

                for item in json_data['items']:
                    title = item.get('title', [''])[0].replace('\n', ' ')
                    abstract = item.get('abstract', '').replace('\n', ' ')
                    url = item.get('URL', '').replace('\n', ' ')

                    file_content.append({
                        'doc_id': self.doc_id,
                        'title': title,
                        'abstract': abstract,
                        'URL': url
                    })

                    self.metadata[self.doc_id] = {
                        'index': len(file_content) - 1,
                        'file': f'documents_{file_count}.gz'
                    }

                    self.doc_id += 1
                    document_counter += 1

                    if document_counter == self.documents_per_file:
                        compressed_data = gzip.compress(json.dumps(file_content).encode('utf-8'))
                        self.documents[f'documents_{file_count}.gz'] = compressed_data
                        file_count += 1
                        file_content = []
                        document_counter = 0

                if file_content:
                    compressed_data = gzip.compress(json.dumps(file_content).encode('utf-8'))
                    self.documents[f'documents_{file_count}.gz'] = compressed_data
                    file_count += 1

                print(f'Loaded document {file} in memory ({counter / total_files * 100:.2f}%)', end="\r", flush=True)
                counter += 1

        if not self.ids_exist:
            self.save_ids()

    def get_title_abstract_url(self, doc_id):
        if doc_id in self.metadata:
            file = self.metadata[doc_id]['file']
            index = self.metadata[doc_id]['index']

            compressed_data = self.documents[file]
            item_data = json.loads(gzip.decompress(compressed_data).decode('utf-8'))

            item = item_data[index]
            return item['title'], item['abstract'], item['URL']
        else:
            return None, None, None

    # TODO: Must return results ordered
    def get_titles_abstracts_urls(self, doc_ids, sort_by_doc_id=False):
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
                index = self.metadata[doc_id]['index']
                item = item_data[index]
                unordered_results.append({
                    "order": doc_id_order[doc_id],
                    "doc_id": doc_id,
                    "title": item['title'],
                    "abstract": item['abstract'],
                    "URL": item['URL']
                })

        # Sort results based on the order of doc_ids in the input or based on doc_ids
        if sort_by_doc_id:
            return sorted(unordered_results, key=lambda x: x['order'])
        else:
            return unordered_results

    def get_all_documents(self):
        all_ids = []
        for i in range(1, self.doc_id):
            all_ids.append(i)
        return self.get_titles_abstracts_urls(all_ids)
