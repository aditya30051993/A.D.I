from pymilvus import Collection, connections, DataType, FieldSchema, CollectionSchema, list_collections

def connect_to_milvus():
    # Connect to the Milvus server (default: localhost:19530)
    connections.connect(alias="default", host="localhost", port="19530")

def create_collection():
    # Define fields for the collection
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
    ]

    # Create a collection schema
    schema = CollectionSchema(fields=fields, description="A collection of vector embeddings")

    # Create a collection if it doesn't already exist
    collection_name = "example_collection"
    
    # Use list_collections() to check if the collection already exists
    if collection_name not in list_collections():
        collection = Collection(name=collection_name, schema=schema)
        collection.create_index(field_name="embedding", index_params={"metric_type": "L2"})
        return collection
    else:
        return Collection(collection_name)

def insert_embeddings(collection, embeddings):
    # Insert data into the Milvus collection
    ids = [i for i in range(len(embeddings))]
    collection.insert([ids, embeddings])
    collection.load()

def search_embeddings(collection, query_embedding, top_k=5):
    # Perform a vector search for the nearest neighbors
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    result = collection.search(
        [query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        expr=None
    )
    return result
