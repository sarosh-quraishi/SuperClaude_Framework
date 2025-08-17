#!/usr/bin/env python3
"""
Clean Code RAG System

Processes Clean Code PDF, creates embeddings, and provides retrieval for Level 1 agent.
"""

import os
import json
import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging

# Default PDF path
DEFAULT_PDF_PATH = "/home/sarosh/Documents/books/CleanCode.pdf"

try:
    # PDF Processing
    import PyPDF2
    import pdfplumber
    
    # Vector Store & Embeddings
    import chromadb
    from sentence_transformers import SentenceTransformer
    
    # Text Processing
    import tiktoken
    import re
    
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  RAG dependencies not installed: {e}")
    print("Run: pip install -r requirements_clean_code.txt")
    DEPENDENCIES_AVAILABLE = False

class CleanCodeRAG:
    """RAG system for Clean Code book knowledge"""
    
    def __init__(self, pdf_path: str = DEFAULT_PDF_PATH, persist_dir: str = None):
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("RAG dependencies not installed. Run: pip install -r requirements_clean_code.txt")
        
        self.pdf_path = pdf_path
        self.persist_dir = persist_dir or str(Path(__file__).parent / "clean_code_knowledge_base")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = 512
        self.chunk_overlap = 50
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection_name = "clean_code_chunks"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from Clean Code PDF with metadata"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        print(f"📖 Extracting text from {pdf_path}...")
        
        pages = []
        
        # Try pdfplumber first (better for structured text)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:  # Filter out mostly empty pages
                        pages.append({
                            "page_number": i + 1,
                            "text": text.strip(),
                            "source": "pdfplumber"
                        })
                        
        except Exception as e:
            self.logger.warning(f"pdfplumber failed: {e}, trying PyPDF2...")
            
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for i, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        pages.append({
                            "page_number": i + 1,
                            "text": text.strip(),
                            "source": "PyPDF2"
                        })
        
        print(f"✅ Extracted {len(pages)} pages with content")
        return pages
    
    def identify_structure(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify chapters, sections, and structure in the Clean Code book"""
        
        structured_pages = []
        current_chapter = "Introduction"
        current_section = "Unknown"
        
        # Clean Code specific chapter patterns
        chapter_patterns = [
            r"Chapter\s+(\d+)[:\s]+(.+)",
            r"(\d+)\s*\.\s*(.+)",  # "2. Meaningful Names"
            r"^(\d+)\s+(.+)$"      # "1 Clean Code"
        ]
        
        # Known Clean Code chapters for reference
        known_chapters = {
            "1": "Clean Code",
            "2": "Meaningful Names", 
            "3": "Functions",
            "4": "Comments",
            "5": "Formatting",
            "6": "Objects and Data Structures",
            "7": "Error Handling",
            "8": "Boundaries",
            "9": "Unit Tests",
            "10": "Classes",
            "11": "Systems",
            "12": "Emergence",
            "13": "Concurrency",
            "14": "Successive Refinement",
            "15": "JUnit Internals",
            "16": "Refactoring SerialDate",
            "17": "Smells and Heuristics"
        }
        
        for page in pages:
            text = page["text"]
            lines = text.split('\n')
            
            # Look for chapter indicators
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                for pattern in chapter_patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        if len(match.groups()) >= 2:
                            chapter_num = match.group(1)
                            chapter_title = match.group(2)
                            current_chapter = f"Chapter {chapter_num}: {chapter_title}"
                        else:
                            # Try to map to known chapters
                            chapter_text = match.group(1)
                            if chapter_text.isdigit() and chapter_text in known_chapters:
                                current_chapter = f"Chapter {chapter_text}: {known_chapters[chapter_text]}"
                            else:
                                current_chapter = chapter_text
                        break
            
            # Look for section indicators (Clean Code has distinctive section headers)
            for line in lines:
                line = line.strip()
                # Clean Code sections often start with capital letters and are short
                if (len(line) > 5 and len(line) < 60 and 
                    line[0].isupper() and 
                    not line.endswith('.') and
                    not any(char.isdigit() for char in line[:3])):  # Not starting with numbers
                    
                    # Some heuristics for Clean Code sections
                    if any(keyword in line.lower() for keyword in [
                        'function', 'variable', 'class', 'method', 'name', 'comment',
                        'small', 'big', 'rule', 'principle', 'example', 'listing'
                    ]):
                        current_section = line
                        break
            
            # Add structure metadata
            page["chapter"] = current_chapter
            page["section"] = current_section
            structured_pages.append(page)
        
        return structured_pages
    
    def chunk_text(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk pages into smaller pieces with overlap for better retrieval"""
        
        chunks = []
        chunk_id = 0
        
        for page in pages:
            text = page["text"]
            
            # Simple sliding window chunking
            words = text.split()
            
            if len(words) <= self.chunk_size:
                # Page is small enough, use as single chunk
                chunks.append({
                    "chunk_id": f"chunk_{chunk_id:04d}",
                    "text": text,
                    "page_number": page["page_number"],
                    "chapter": page["chapter"],
                    "section": page["section"],
                    "start_word": 0,
                    "end_word": len(words),
                    "source": page["source"]
                })
                chunk_id += 1
            else:
                # Split into overlapping chunks
                start = 0
                while start < len(words):
                    end = min(start + self.chunk_size, len(words))
                    chunk_words = words[start:end]
                    chunk_text = " ".join(chunk_words)
                    
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_id:04d}",
                        "text": chunk_text,
                        "page_number": page["page_number"],
                        "chapter": page["chapter"],
                        "section": page["section"],
                        "start_word": start,
                        "end_word": end,
                        "source": page["source"]
                    })
                    
                    chunk_id += 1
                    start += (self.chunk_size - self.chunk_overlap)
        
        print(f"📝 Created {len(chunks)} text chunks")
        return chunks
    
    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create embeddings for all chunks"""
        
        print(f"🔮 Creating embeddings for {len(chunks)} chunks...")
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()
        
        print("✅ Embeddings created successfully")
        return chunks
    
    def build_knowledge_base(self, pdf_path: str = None) -> str:
        """Build complete knowledge base from Clean Code PDF"""
        
        pdf_path = pdf_path or self.pdf_path
        
        print("🏗️  Building Clean Code Knowledge Base...")
        print(f"📖 Using PDF: {pdf_path}")
        
        # Extract text
        pages = self.extract_text_from_pdf(pdf_path)
        
        # Identify structure
        structured_pages = self.identify_structure(pages)
        
        # Create chunks
        chunks = self.chunk_text(structured_pages)
        
        # Create embeddings
        chunks_with_embeddings = self.create_embeddings(chunks)
        
        # Store in ChromaDB
        self.store_in_vector_db(chunks_with_embeddings)
        
        # Save metadata
        metadata = {
            "pdf_path": pdf_path,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedding_model": "all-MiniLM-L6-v2",
            "created_at": str(Path(pdf_path).stat().st_mtime)
        }
        
        metadata_path = Path(self.persist_dir) / "metadata.json"
        metadata_path.parent.mkdir(exist_ok=True)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Knowledge base built successfully at {self.persist_dir}")
        return self.persist_dir
    
    def store_in_vector_db(self, chunks: List[Dict[str, Any]]) -> None:
        """Store chunks in ChromaDB vector database"""
        
        print("💾 Storing chunks in vector database...")
        
        # Try to get existing collection or create new one
        try:
            collection = self.chroma_client.get_collection(self.collection_name)
            # Clear existing data
            collection.delete()
        except:
            pass
        
        collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"description": "Clean Code book chunks with embeddings"}
        )
        
        # Prepare data for ChromaDB
        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        embeddings = [chunk["embedding"] for chunk in chunks]
        metadatas = [
            {
                "page_number": chunk["page_number"],
                "chapter": chunk["chapter"],
                "section": chunk["section"],
                "start_word": chunk["start_word"],
                "end_word": chunk["end_word"],
                "source": chunk["source"]
            }
            for chunk in chunks
        ]
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))
            
            collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
        
        print(f"✅ Stored {len(chunks)} chunks in vector database")
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve most relevant chunks for a query"""
        
        if not self.is_knowledge_base_ready():
            # Try to build automatically if PDF exists
            if os.path.exists(self.pdf_path):
                print(f"🔄 Building knowledge base from {self.pdf_path}...")
                self.build_knowledge_base()
            else:
                raise ValueError(f"Knowledge base not ready and PDF not found at {self.pdf_path}")
        
        # Get collection
        collection = self.chroma_client.get_collection(self.collection_name)
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        relevant_chunks = []
        for i in range(len(results['ids'][0])):
            chunk = {
                "chunk_id": results['ids'][0][i],
                "text": results['documents'][0][i],
                "distance": results['distances'][0][i],
                "metadata": results['metadatas'][0][i]
            }
            relevant_chunks.append(chunk)
        
        return relevant_chunks
    
    def is_knowledge_base_ready(self) -> bool:
        """Check if knowledge base exists and is ready"""
        try:
            collection = self.chroma_client.get_collection(self.collection_name)
            count = collection.count()
            return count > 0
        except:
            return False
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get information about the knowledge base"""
        metadata_path = Path(self.persist_dir) / "metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        if self.is_knowledge_base_ready():
            collection = self.chroma_client.get_collection(self.collection_name)
            metadata["chunk_count"] = collection.count()
            metadata["status"] = "ready"
        else:
            metadata["status"] = "not_ready"
        
        return metadata


# Singleton instance for global use
_rag_instance = None

def get_clean_code_rag() -> CleanCodeRAG:
    """Get or create CleanCodeRAG singleton instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = CleanCodeRAG()
    return _rag_instance


async def setup_clean_code_rag(pdf_path: str = DEFAULT_PDF_PATH) -> CleanCodeRAG:
    """Setup RAG system with Clean Code PDF"""
    
    print("🚀 Setting up Clean Code RAG System...")
    
    rag = CleanCodeRAG(pdf_path)
    
    if not rag.is_knowledge_base_ready():
        if os.path.exists(pdf_path):
            print("📚 Knowledge base not found, building from PDF...")
            rag.build_knowledge_base(pdf_path)
        else:
            print(f"⚠️  PDF not found at {pdf_path}")
            print("Knowledge base will be built when PDF is available")
    else:
        print("✅ Knowledge base already exists")
    
    return rag


if __name__ == "__main__":
    import sys
    
    pdf_path = DEFAULT_PDF_PATH
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    async def main():
        rag = await setup_clean_code_rag(pdf_path)
        
        if rag.is_knowledge_base_ready():
            # Test retrieval
            test_queries = [
                "function should do one thing",
                "meaningful names intention revealing",
                "comments bad code rewrite"
            ]
            
            for query in test_queries:
                print(f"\n🔍 Test Query: '{query}'")
                results = rag.retrieve_relevant_chunks(query, n_results=2)
                
                print("📖 Top Results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. Chapter: {result['metadata']['chapter']}")
                    print(f"   Section: {result['metadata']['section']}")
                    print(f"   Page: {result['metadata']['page_number']}")
                    print(f"   Distance: {result['distance']:.3f}")
                    print(f"   Text: {result['text'][:150]}...")
        else:
            print("❌ Knowledge base not ready")
    
    asyncio.run(main())