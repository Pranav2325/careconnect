# backend/services/document_service.py
# Handles PDF upload, text extraction, chunking, and ChromaDB storage + search

import chromadb
from chromadb.config import Settings
import pypdf
import io
import os
from dotenv import load_dotenv

load_dotenv()

# Folder where ChromaDB stores all vector data permanently
CHROMA_DB_PATH = "./chroma_db"


class DocumentService:
    def __init__(self):
        """
        Initialize ChromaDB client.

        PersistentClient = data is saved on disk (not lost after restart).
        """
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

        # Prefix used to create separate collections per patient
        # Example: patient_1, patient_2, etc.
        self.collection_prefix = "patient_"

    def get_collection(self, patient_id: int):
        """
        Get or create a ChromaDB collection for a specific patient.

        Each patient has isolated storage so their medical data never mixes.
        """
        collection_name = f"{self.collection_prefix}{patient_id}"

        return self.client.get_or_create_collection(
            name=collection_name,
            # Cosine similarity is best for text because it compares meaning direction
            metadata={"hnsw:space": "cosine"}
        )

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """
        Convert PDF bytes into readable text.

        FastAPI gives uploaded files as bytes, so we read directly from memory.
        """
        pdf_file = io.BytesIO(file_bytes)  # treat bytes like a file
        reader = pypdf.PdfReader(pdf_file)  # open PDF in memory

        full_text = ""

        # Read each page and extract text
        for page in reader.pages:
            page_text = page.extract_text()

            # Some PDFs may have empty pages
            if page_text:
                full_text += page_text + "\n"

        return full_text

    def split_into_chunks(self, text: str, chunk_size: int = 500) -> list[str]:
        """
        Split long text into smaller overlapping chunks.

        Why chunking?
        - AI embeddings work better on smaller pieces
        - Improves search accuracy

        Why overlap?
        - Prevents loss of meaning at boundaries between chunks
        """
        words = text.split()
        chunks = []

        overlap = 50  # number of words shared between consecutive chunks

        # Slide through words with overlap to preserve context
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])

            if chunk:  # avoid empty chunks
                chunks.append(chunk)

        return chunks

    def add_document(self, patient_id: int, file_bytes: bytes, filename: str) -> dict:
        """
        Full ingestion pipeline:
        PDF → Text → Chunks → Embeddings → ChromaDB storage

        Each chunk is stored with:
        - Unique ID (for tracking)
        - Text content (for retrieval)
        - Metadata (for filtering & traceability)
        """

        # Step 1: Extract raw text from PDF
        text = self.extract_text_from_pdf(file_bytes)

        # If PDF has no readable text, stop processing
        if not text.strip():
            return {"error": "Could not extract text from PDF"}

        # Step 2: Convert long text into smaller chunks
        chunks = self.split_into_chunks(text)

        # Step 3: Get patient-specific vector database
        collection = self.get_collection(patient_id)

        # Create unique IDs for each chunk
        # Example: report.pdf_chunk0, report.pdf_chunk1
        ids = [f"{filename}_chunk{i}" for i in range(len(chunks))]

        # Metadata helps track origin of each chunk
        # Useful for debugging, filtering, and traceability
        metadatas = [
            {
                "filename": filename,
                "patient_id": patient_id,
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]

        # Step 4: Store data in ChromaDB (text + ids + metadata)
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )

        # Return summary of what was stored
        return {
            "filename": filename,
            "chunks_stored": len(chunks),
            "characters_extracted": len(text)
        }

    def search_documents(self, patient_id: int, query: str, n_results: int = 3) -> list[dict]:
        """
        Semantic search inside a patient's documents.

        Converts query into embedding vector and finds most similar chunks.
        """

        # Get patient-specific collection
        collection = self.get_collection(patient_id)

        # If no documents exist, return empty result
        if collection.count() == 0:
            return []

        # Query ChromaDB using semantic search
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count())
        )

        # Format results into clean output
        formatted = []

        for i, doc in enumerate(results["documents"][0]):
            formatted.append({
                "text": doc,
                "filename": results["metadatas"][0][i]["filename"],
                "relevance_rank": i + 1  # rank by similarity
            })

        return formatted


# Global singleton instance used across the application
document_service = DocumentService()