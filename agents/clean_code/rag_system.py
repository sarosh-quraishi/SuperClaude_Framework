#!/usr/bin/env python3
"""
Clean Code RAG System

Processes Clean Code PDF, creates embeddings, and provides retrieval for Level 1 agent.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import re
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
    
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  RAG dependencies not installed: {e}")
    print("Run: pip install -r requirements_clean_code.txt")
    DEPENDENCIES_AVAILABLE = False

class CleanCodeRAG:
    """RAG system for Clean Code book knowledge"""
    
    # Content validation thresholds
    MIN_PAGE_CONTENT_LENGTH = 50
    MIN_SECTION_TITLE_LENGTH = 5
    MAX_SECTION_TITLE_LENGTH = 60
    
    # Processing parameters
    VECTOR_DB_BATCH_SIZE = 100
    DEFAULT_CHUNK_SIZE = 512
    DEFAULT_CHUNK_OVERLAP = 50
    STRUCTURE_DETECTION_LINES = 10
    CHAPTER_PATTERN_CHECK_LINES = 3
    
    # Embedding model configuration
    DEFAULT_EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    DEFAULT_RETRIEVAL_RESULTS = 5
    
    def __init__(self, pdf_path: str = DEFAULT_PDF_PATH, persist_dir: Optional[str] = None) -> None:
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "RAG dependencies not installed. Required packages: chromadb, sentence-transformers, "
                "pdfplumber, PyPDF2, tiktoken. Install with: pip install -r requirements_clean_code.txt"
            )
        
        self.pdf_path = pdf_path
        self.persist_dir = persist_dir or str(Path(__file__).parent / "clean_code_knowledge_base")
        self.embedding_model = SentenceTransformer(self.DEFAULT_EMBEDDING_MODEL)
        self.chunk_size = self.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = self.DEFAULT_CHUNK_OVERLAP
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection_name = "clean_code_chunks"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from Clean Code PDF with metadata.
        
        Args:
            pdf_path: Path to the PDF file to extract text from
            
        Returns:
            List of dictionaries containing page text, page number, and source
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist at specified path
        """
        self._validate_pdf_exists(pdf_path)
        print(f"📖 Extracting text from {pdf_path}...")
        
        pages = self._extract_with_fallback_strategy(pdf_path)
        
        print(f"✅ Extracted {len(pages)} pages with content")
        return pages
    
    def _validate_pdf_exists(self, pdf_path: str) -> None:
        """Validate that PDF file exists at the given path.
        
        Args:
            pdf_path: Path to the PDF file to validate
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(
                f"Clean Code PDF not found at: {pdf_path}. "
                f"Please ensure the PDF exists at this location or update DEFAULT_PDF_PATH. "
                f"You can download Clean Code by Robert C. Martin from your preferred book retailer."
            )
    
    def _extract_with_fallback_strategy(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text using pdfplumber with PyPDF2 fallback"""
        try:
            return self._extract_with_pdfplumber(pdf_path)
        except Exception as extraction_error:
            self.logger.warning(f"pdfplumber failed: {extraction_error}, trying PyPDF2...")
            return self._extract_with_pypdf2(pdf_path)
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text using pdfplumber library"""
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages):
                text = page.extract_text()
                if self._is_valid_page_content(text):
                    pages.append(self._create_page_metadata(page_index + 1, text, "pdfplumber"))
        return pages
    
    def _extract_with_pypdf2(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text using PyPDF2 library as fallback"""
        pages = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_index, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if self._is_valid_page_content(text):
                    pages.append(self._create_page_metadata(page_index + 1, text, "PyPDF2"))
        return pages
    
    def _is_valid_page_content(self, text: str) -> bool:
        """Check if page content meets minimum length requirements"""
        return text and len(text.strip()) > self.MIN_PAGE_CONTENT_LENGTH
    
    def _create_page_metadata(self, page_number: int, text: str, source: str) -> Dict[str, Any]:
        """Create standardized page metadata dictionary"""
        return {
            "page_number": page_number,
            "text": text.strip(),
            "source": source
        }
    
    def identify_structure(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify chapters, sections, and structure in the Clean Code book.
        
        Args:
            pages: List of page dictionaries with text content
            
        Returns:
            List of pages with added chapter and section metadata
        """
        
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
            chapter_found = self._extract_chapter_from_page(page["text"], chapter_patterns, known_chapters)
            if chapter_found:
                current_chapter = chapter_found
            
            section_found = self._extract_section_from_page(page["text"])
            if section_found:
                current_section = section_found
            
            page_with_structure = self._add_structure_metadata(page, current_chapter, current_section)
            structured_pages.append(page_with_structure)
        
        return structured_pages
    
    def _extract_chapter_from_page(self, text: str, chapter_patterns: List[str], known_chapters: Dict[str, str]) -> Optional[str]:
        """Extract chapter information from page text"""
        lines = text.split('\n')[:self.STRUCTURE_DETECTION_LINES]
        
        for line in lines:
            chapter = self._match_chapter_patterns(line.strip(), chapter_patterns, known_chapters)
            if chapter:
                return chapter
        
        return None
    
    def _match_chapter_patterns(self, line: str, patterns: List[str], known_chapters: Dict[str, str]) -> Optional[str]:
        """Match line against chapter patterns"""
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return self._format_chapter_match(match, known_chapters)
        
        return None
    
    def _format_chapter_match(self, match: re.Match, known_chapters: Dict[str, str]) -> str:
        """Format matched chapter information"""
        if len(match.groups()) >= 2:
            chapter_num = match.group(1)
            chapter_title = match.group(2)
            return f"Chapter {chapter_num}: {chapter_title}"
        else:
            chapter_text = match.group(1)
            if chapter_text.isdigit() and chapter_text in known_chapters:
                return f"Chapter {chapter_text}: {known_chapters[chapter_text]}"
            else:
                return chapter_text
    
    def _extract_section_from_page(self, text: str) -> Optional[str]:
        """Extract section information from page text"""
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if self._is_valid_section_line(line):
                return line
        
        return None
    
    def _is_valid_section_line(self, line: str) -> bool:
        """Check if line is a valid section header"""
        if not (self.MIN_SECTION_TITLE_LENGTH < len(line) < self.MAX_SECTION_TITLE_LENGTH):
            return False
        
        if not (line[0].isupper() and not line.endswith('.')):
            return False
        
        if any(char.isdigit() for char in line[:self.CHAPTER_PATTERN_CHECK_LINES]):
            return False
        
        return self._contains_section_keywords(line)
    
    def _contains_section_keywords(self, line: str) -> bool:
        """Check if line contains Clean Code section keywords"""
        section_keywords = [
            'function', 'variable', 'class', 'method', 'name', 'comment',
            'small', 'big', 'rule', 'principle', 'example', 'listing'
        ]
        return any(keyword in line.lower() for keyword in section_keywords)
    
    def _add_structure_metadata(self, page: Dict[str, Any], chapter: str, section: str) -> Dict[str, Any]:
        """Add structure metadata to page"""
        page["chapter"] = chapter
        page["section"] = section
        return page
    
    def chunk_text(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk pages into smaller pieces with overlap for better retrieval.
        
        Args:
            pages: List of page dictionaries with structure metadata
            
        Returns:
            List of text chunks with metadata for vector storage
        """
        chunks = []
        chunk_id = 0
        
        for page in pages:
            page_chunks = self._create_chunks_for_page(page, chunk_id)
            chunks.extend(page_chunks)
            chunk_id += len(page_chunks)
        
        print(f"📝 Created {len(chunks)} text chunks")
        return chunks
    
    def _create_chunks_for_page(self, page: Dict[str, Any], starting_chunk_id: int) -> List[Dict[str, Any]]:
        """Create chunks for a single page.
        
        Args:
            page: Page dictionary with text and metadata
            starting_chunk_id: Starting ID for chunk numbering
            
        Returns:
            List of chunks created from the page
        """
        text = page["text"]
        words = text.split()
        chunks = []
        chunk_id = starting_chunk_id
        
        if len(words) <= self.chunk_size:
            # Page is small enough, use as single chunk
            chunk = self._create_single_chunk(page, text, 0, len(words), chunk_id)
            chunks.append(chunk)
        else:
            # Split into overlapping chunks
            chunks = self._create_overlapping_chunks(page, words, chunk_id)
        
        return chunks
    
    def _create_single_chunk(self, page: Dict[str, Any], text: str, start_word: int, end_word: int, chunk_id: int) -> Dict[str, Any]:
        """Create a single chunk with metadata.
        
        Args:
            page: Source page metadata
            text: Text content for the chunk
            start_word: Starting word index
            end_word: Ending word index
            chunk_id: Unique chunk identifier
            
        Returns:
            Chunk dictionary with metadata
        """
        return {
            "chunk_id": f"chunk_{chunk_id:04d}",
            "text": text,
            "page_number": page["page_number"],
            "chapter": page["chapter"],
            "section": page["section"],
            "start_word": start_word,
            "end_word": end_word,
            "source": page["source"]
        }
    
    def _create_overlapping_chunks(self, page: Dict[str, Any], words: List[str], starting_chunk_id: int) -> List[Dict[str, Any]]:
        """Create overlapping chunks from a list of words.
        
        Args:
            page: Source page metadata
            words: List of words to chunk
            starting_chunk_id: Starting ID for chunk numbering
            
        Returns:
            List of overlapping chunks
        """
        chunks = []
        chunk_id = starting_chunk_id
        start = 0
        
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunk = self._create_single_chunk(page, chunk_text, start, end, chunk_id)
            chunks.append(chunk)
            
            chunk_id += 1
            start += (self.chunk_size - self.chunk_overlap)
        
        return chunks
    
    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create embeddings for all text chunks.
        
        Args:
            chunks: List of text chunks to create embeddings for
            
        Returns:
            List of chunks with added embedding vectors
        """
        
        print(f"🔮 Creating embeddings for {len(chunks)} chunks...")
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Add embeddings to chunks
        for chunk_index, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[chunk_index].tolist()
        
        print("✅ Embeddings created successfully")
        return chunks
    
    def build_knowledge_base(self, pdf_path: Optional[str] = None) -> str:
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
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
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
        except Exception as collection_error:
            self.logger.debug(f"Collection {self.collection_name} doesn't exist or failed to delete: {collection_error}")
        
        collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"description": "Clean Code book chunks with embeddings"}
        )
        
        # Prepare data for ChromaDB
        ids, documents, embeddings, metadatas = self._prepare_vector_db_data(chunks)
        
        # Add to collection in batches
        batch_size = self.VECTOR_DB_BATCH_SIZE
        for batch_start in range(0, len(chunks), batch_size):
            batch_end = min(batch_start + batch_size, len(chunks))
            
            collection.add(
                ids=ids[batch_start:batch_end],
                embeddings=embeddings[batch_start:batch_end],
                documents=documents[batch_start:batch_end],
                metadatas=metadatas[batch_start:batch_end]
            )
        
        print(f"✅ Stored {len(chunks)} chunks in vector database")
    
    def _prepare_vector_db_data(self, chunks: List[Dict[str, Any]]) -> Tuple[List[str], List[str], List[List[float]], List[Dict[str, Any]]]:
        """Prepare chunk data for ChromaDB storage.
        
        Args:
            chunks: List of text chunks with embeddings and metadata
            
        Returns:
            Tuple of (ids, documents, embeddings, metadatas) for ChromaDB
        """
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
        return ids, documents, embeddings, metadatas
    
    def retrieve_relevant_chunks(self, query: str, n_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve most relevant chunks for a query.
        
        Args:
            query: Text query to search for
            n_results: Number of results to return (default: DEFAULT_RETRIEVAL_RESULTS)
            
        Returns:
            List of relevant chunks with similarity scores
            
        Raises:
            ValueError: If knowledge base is not ready and PDF not found
        """
        
        if not self.is_knowledge_base_ready():
            # Try to build automatically if PDF exists
            if os.path.exists(self.pdf_path):
                print(f"🔄 Building knowledge base from {self.pdf_path}...")
                self.build_knowledge_base()
            else:
                raise ValueError(
                    f"Knowledge base not ready and PDF not found at {self.pdf_path}. "
                    f"To fix this: 1) Ensure PDF exists at the specified path, "
                    f"2) Run build_knowledge_base() to create embeddings, or "
                    f"3) Update pdf_path to point to your Clean Code PDF location."
                )
        
        # Get collection
        collection = self.chroma_client.get_collection(self.collection_name)
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search with default results count if not specified
        results_count = n_results or self.DEFAULT_RETRIEVAL_RESULTS
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=results_count
        )
        
        # Format results
        return self._format_search_results(results)
    
    def _format_search_results(self, results: Dict) -> List[Dict[str, Any]]:
        """Format ChromaDB search results into structured format.
        
        Args:
            results: Raw results from ChromaDB query
            
        Returns:
            List of formatted result dictionaries
        """
        relevant_chunks = []
        for result_index in range(len(results['ids'][0])):
            chunk = {
                "chunk_id": results['ids'][0][result_index],
                "text": results['documents'][0][result_index],
                "distance": results['distances'][0][result_index],
                "metadata": results['metadatas'][0][result_index]
            }
            relevant_chunks.append(chunk)
        return relevant_chunks
    
    def is_knowledge_base_ready(self) -> bool:
        """Check if knowledge base exists and is ready"""
        try:
            collection = self.chroma_client.get_collection(self.collection_name)
            count = collection.count()
            return count > 0
        except Exception as collection_error:
            self.logger.debug(f"Failed to check knowledge base status: {collection_error}")
            return False
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get information about the knowledge base"""
        metadata_path = Path(self.persist_dir) / "metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
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

def get_clean_code_rag() -> 'CleanCodeRAG':
    """Get or create CleanCodeRAG singleton instance.
    
    Returns:
        Singleton instance of CleanCodeRAG
    """
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = CleanCodeRAG()
    return _rag_instance


async def setup_clean_code_rag(pdf_path: str = DEFAULT_PDF_PATH) -> 'CleanCodeRAG':
    """Setup RAG system with Clean Code PDF.
    
    Args:
        pdf_path: Path to the Clean Code PDF file
        
    Returns:
        Configured CleanCodeRAG instance
    """
    
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
                for result_number, result in enumerate(results, 1):
                    print(f"\n{result_number}. Chapter: {result['metadata']['chapter']}")
                    print(f"   Section: {result['metadata']['section']}")
                    print(f"   Page: {result['metadata']['page_number']}")
                    print(f"   Distance: {result['distance']:.3f}")
                    print(f"   Text: {result['text'][:150]}...")
        else:
            print("❌ Knowledge base not ready")
    
    asyncio.run(main())