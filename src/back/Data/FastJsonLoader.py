import os
import json
import gzip


class FastJsonLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.documents = {}
        self.metadata = {}
        self.doc_id = 1

    def load_documents(self):
        counter = 1
        total_files = len([f for f in os.listdir(self.folder_path) if f.endswith(".gz")])
        for file in os.listdir(self.folder_path):
            if file.endswith('.gz'):
                file_path = os.path.join(self.folder_path, file)
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    json_data = json.load(f)

                file_content = []
                for item in json_data['items']:
                    title = ' '
                    abstract = ' '
                    url = ' '
                    try:
                        title = item['title'][0].replace('\n', ' ')
                    except KeyError:
                        pass
                    try:
                        abstract = item['abstract'].replace('\n', ' ')
                    except KeyError:
                        pass
                    try:
                        url = item['URL'].replace('\n', ' ')
                    except KeyError:
                        pass


                    file_content.extend([str(self.doc_id), title, abstract, url])

                    self.metadata[self.doc_id] = {
                        'line_number': self.doc_id * 4 - 3,
                        'file': file
                    }

                    self.doc_id += 1
                compressed_data = gzip.compress('\n'.join(file_content).encode('utf-8'))
                self.documents[file] = compressed_data
                print(f'Loaded document {file} in memory ({counter / total_files * 100:.2f}%)')
                counter += 1

    def get_title_abstract_url(self, doc_id):
        if doc_id in self.metadata:
            file = self.metadata[doc_id]['file']
            line_number = self.metadata[doc_id]['line_number']

            compressed_data = self.documents[file]
            item_data = gzip.decompress(compressed_data).decode('utf-8').split('\n')

            title = item_data[line_number + 1]
            abstract = item_data[line_number + 2]
            url = item_data[line_number + 3]

            return title, abstract, url
        else:
            return None, None, None

    def get_titles_abstracts_urls(self, doc_ids):
        results = []
        file_buckets = {}

        # Create buckets for doc_ids belonging to the same file
        for doc_id in doc_ids:
            if doc_id in self.metadata:
                file = self.metadata[doc_id]['file']
                if file not in file_buckets:
                    file_buckets[file] = []
                file_buckets[file].append(doc_id)

        results = list()

        # Retrieve titles and abstracts for each bucket
        for file, bucket_doc_ids in file_buckets.items():
            compressed_data = self.documents[file]
            item_data = gzip.decompress(compressed_data).decode('utf-8').split('\n')

            for doc_id in bucket_doc_ids:
                line_number = self.metadata[doc_id]['line_number'] % 15000
                title = item_data[line_number]
                abstract = item_data[line_number + 1]
                url = item_data[line_number + 2]
                results.append({"doc_id": doc_id, "title": title, "abstract": abstract, "URL": url})

        return results

    def get_all_documents(self):
        all_ids = []
        for i in range(1, self.doc_id):
            all_ids.append(i)
        return self.get_titles_abstracts_urls(all_ids)
