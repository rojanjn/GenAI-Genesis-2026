from backend.db.firebase_client import init_firebase
from backend.db.queries import save_entry
from backend.embeddings.embedding_service import generate_embedding

def main():
    init_firebase()

    user_id = "test_user"

    entries = [
        "I have been really stressed about my midterms and deadlines lately.",
        "School has been overwhelming and I feel behind on assignments.",
        "I am anxious about exams and keeping up with coursework.",
        "My workload feels too heavy right now and I do not know where to start.",
    ]

    for text in entries:
        embedding = generate_embedding(text)
        entry_id = save_entry(user_id, text, embedding)
        print(f"Saved entry: {entry_id} | {text}")

if __name__ == "__main__":
    main()