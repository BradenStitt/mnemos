from pinecone import Pinecone
import time
from tqdm import tqdm
from settings import settings

def main():
    pc = Pinecone(api_key=settings.pinecone_api_key, source_tag="pinecone:fastapi_pinecone_async_example")

    dense_index = create_index(pc, settings.pinecone_dense_index_name, settings.dense_embedding_model)
    sparse_index = create_index(pc, settings.pinecone_sparse_index_name, settings.sparse_embedding_model)

    # Create test data manually
    records = create_test_records()
    
    upsert_data(dense_index, settings.pinecone_namespace, records)
    upsert_data(sparse_index, settings.pinecone_namespace, records)
    
    time.sleep(15)

    stats = dense_index.describe_index_stats()
    print("Dense index stats:", stats)

    stats = sparse_index.describe_index_stats()
    print("Sparse index stats:", stats)

def create_index(pc, index_name, embed_model):
    if not pc.has_index(index_name):
        pc.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": embed_model,
                "field_map": {"text": "chunk_text"}
            }
        )

    return pc.Index(index_name)

def create_test_records():
    """Create manual test data for Pinecone"""
    test_data = [
        {
            "id": "doc1",
            "content": "The quick brown fox jumps over the lazy dog. This is a classic pangram used for testing. It contains every letter of the alphabet."
        },
        {
            "id": "doc2",
            "content": "Machine learning is a subset of artificial intelligence. It focuses on the use of data and algorithms to imitate the way humans learn. Deep learning is a type of machine learning."
        },
        {
            "id": "doc3",
            "content": "Python is a high-level programming language. It is widely used for web development, data science, and automation. Python has a simple and readable syntax."
        },
        {
            "id": "doc4",
            "content": "Basketball is a team sport played on a rectangular court. Two teams of five players try to score by shooting a ball through a hoop. The game was invented in 1891."
        },
        {
            "id": "doc5",
            "content": "Climate change refers to long-term shifts in global temperatures. It is primarily caused by human activities. Rising sea levels and extreme weather events are major concerns."
        },
        {
            "id": "doc6",
            "content": "The solar system consists of the Sun and everything that orbits it. This includes eight planets, their moons, and countless asteroids. Earth is the third planet from the Sun."
        },
        {
            "id": "doc7",
            "content": "Coffee is one of the most popular beverages worldwide. It is made from roasted coffee beans. The caffeine in coffee helps people stay alert and focused."
        },
        {
            "id": "doc8",
            "content": "Electric vehicles use electric motors for propulsion. They are powered by rechargeable battery packs. EVs produce zero direct emissions and are considered environmentally friendly."
        },
        {
            "id": "doc9",
            "content": "The internet is a global network of interconnected computers. It enables communication and information sharing worldwide. The World Wide Web was invented in 1989."
        },
        {
            "id": "doc10",
            "content": "Photosynthesis is the process used by plants to convert light energy. They transform carbon dioxide and water into glucose and oxygen. This process is essential for life on Earth."
        }
    ]
    
    records = []
    for doc in test_data:
        # Split content into sentences for chunking
        sentences = doc["content"].split(". ")
        for chunk_id, sentence in enumerate(sentences):
            if sentence.strip():  # Skip empty sentences
                record = {
                    "_id": f"{doc['id']}#{chunk_id}",
                    "chunk_text": sentence.strip() + ("." if not sentence.endswith(".") else "")
                }
                records.append(record)
    
    print(f"Created {len(records)} test records")
    return records

def upsert_data(index, namespace, records):
    # Batch size is limited by the embedding model limit and the API's upsert limit.
    batch_size = 96
    for i in tqdm(range(0, len(records), batch_size), desc="Upserting records to Pinecone"):
        batch = records[i:i + batch_size]
        try:
            index.upsert_records(namespace=namespace, records=batch)
        except Exception as e:
            print(f"Error upserting batch: {e}")
            print(f"Batch: {batch}")

if __name__ == "__main__":
    main()