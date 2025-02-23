from chromadb import PersistentClient, Collection
import ollama


def prepare_db(path: str, collection_name: str) -> Collection:
    """
    Either get or create collection with name `collection_name` in directory `path`.
    """
    chroma_client = PersistentClient(path)
    if collection_name in chroma_client.list_collections():
        print(f"Collection `{collection_name}` found!")
        return chroma_client.get_collection(collection_name)
    print(f"Created collection `{collection_name}`")
    return chroma_client.create_collection(collection_name)

def setup_mock_db(collection: Collection) -> None:
    """
    Populate database with dummy documents.
    """
    documents = [
        "The store opens at 11 on weekends",
        "The store opens at 9 on week days",
        "The store closes at 3pm",
        "The store manager is called Steve",
        "Bob goes to the store every week"
    ]
    ids = [f'fact_{i}' for i in range(len(documents))]
    collection.add(
        documents=documents,
        ids=ids
    )

def get_context(collection: Collection, query: str, num_retrievals = 3) -> str:
    """
    Get relevant documents formatted into paragraph.
    """
    documents = collection.query(query_texts=query, n_results=num_retrievals).get("documents", [[]]) # Extract documents from our query
    return "\n".join(documents[0]) # Only return first batch results (single query)

if __name__ == "__main__":

    DATABASE_PATH = "./data/"
    COLLECTION_NAME = "test_collection"
    MODEL="llama3.2"
    POPULATE_DB = True # NOTE: This should ONLY be ran once. Otherwise documents with duplicate IDs will be inserted and you'll get an annoying message on each query.

    collection = prepare_db(DATABASE_PATH, COLLECTION_NAME)

    if POPULATE_DB:
        print('Populating database with dummy documents..')
        setup_mock_db(collection)

    while True:
        query = input("\n> ")
        context_formatted = get_context(collection, query)

        # Create custom prompt template (I found that the repetition of the query provided best results. This is a matter of prompt engineering.)
        system_template = f"""
        Use the following pieces of context to answer the question at the end.
        If the question does not pertain to the context, answer it normally disregarding the context.
        You should never refer to the fact that you have been provided context.
        
        Context: {context_formatted}
        
        Question: {query}
        
        Answer:
        """

        response = ollama.chat(model=MODEL, messages=[
            {'role': 'system', 'content': f'{system_template}'},
            {'role': 'user', 'content': query}
        ],
            stream=True
        )

        for chunk in response:
            print(chunk['message']['content'], end='', flush=True)