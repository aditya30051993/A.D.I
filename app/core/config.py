from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility

MILVUS_HOST = 'localhost'
MILVUS_PORT = '19530'
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

collection_name = 'pdf_documents'

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
]

schema = CollectionSchema(fields=fields, description="Schema for PDF document embeddings")

if not utility.has_collection(collection_name):
    collection = Collection(name=collection_name, schema=schema)
else:
    collection = Collection(name=collection_name)
