from Preprocessor.DataCleaner import DataCleaner
import DataReader
from Indexer.IndexValueInfo import InfoClass
import pprint

mongoConnection = DataReader.Reader('mongodb://m151User:YyKOhV1xa3mnmlFP@vmi1224404.contaboserver.net:27017/?authMechanism=DEFAULT&authSource=M151')
collection = mongoConnection.getCollection("M151", "Papers")
results = mongoConnection.readCollection(collection)

# presults = list(results)
# for result in presults:
#     print(result)

index_dictionary = dict()
cleaner = DataCleaner()


def nodeAdder(_id, _value, _counter, _index_dictionary, type):
    cleaned_words = cleaner.cleanData(_value)
    for word in cleaned_words:
        _listNode = InfoClass(type, _counter, _id)
        if word in _index_dictionary:
            _index_dictionary[word].append(_listNode)
        else:
            _index_dictionary[word] = [_listNode]
        _counter += 1
    return _counter, _index_dictionary


for doc in results:
    doc_id = doc["_id"]
    for field, value in doc.items():
        counter = 1
        if field == "title":
            counter, index_dictionary = nodeAdder(doc_id, value[0], counter, index_dictionary, "title")
        elif field == "abstract":
            counter, index_dictionary = nodeAdder(doc_id, value, counter, index_dictionary, "abstract")

# for i in index_dictionary.values():
#     pprint.pprint(i[0])
# pprint.pprint(index_dictionary)
# for key, value in index_dictionary.items():
#     print("key: \"", key, "\", value: \"", value[0]._type, "\"")
#
# print()
# print(len(index_dictionary))
