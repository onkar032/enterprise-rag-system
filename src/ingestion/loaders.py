"""Document loaders for various file formats."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class Document:
    """Document class to store content and metadata."""

    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Initialize document."""
        self.content = content
        self.metadata = metadata or {}
        self.metadata.setdefault("source", "unknown")
        self.metadata.setdefault("type", "text")

    def __repr__(self) -> str:
        """String representation."""
        return f"Document(content_length={len(self.content)}, metadata={self.metadata})"


class DocumentLoader(ABC):
    """Abstract base class for document loaders."""

    @abstractmethod
    def load(self, source: str) -> List[Document]:
        """Load documents from source."""
        pass

    def extract_metadata(self, source: str, **kwargs) -> Dict[str, Any]:
        """Extract metadata from source."""
        return {
            "source": source,
            "loader": self.__class__.__name__,
            **kwargs
        }


class PDFLoader(DocumentLoader):
    """Load documents from PDF files."""

    def load(self, source: str) -> List[Document]:
        """Load PDF document."""
        try:
            logger.info(f"Loading PDF: {source}")
            reader = PdfReader(source)
            documents = []

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    metadata = self.extract_metadata(
                        source,
                        page=page_num + 1,
                        total_pages=len(reader.pages),
                        type="pdf"
                    )
                    documents.append(Document(content=text, metadata=metadata))

            logger.info(f"Loaded {len(documents)} pages from PDF")
            return documents

        except Exception as e:
            logger.error(f"Error loading PDF {source}: {e}")
            raise


class TextLoader(DocumentLoader):
    """Load documents from text files."""

    def load(self, source: str) -> List[Document]:
        """Load text document."""
        try:
            logger.info(f"Loading text file: {source}")
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata = self.extract_metadata(source, type="text")
            return [Document(content=content, metadata=metadata)]

        except Exception as e:
            logger.error(f"Error loading text file {source}: {e}")
            raise


class HTMLLoader(DocumentLoader):
    """Load documents from HTML files."""

    def __init__(self, extract_links: bool = False):
        """Initialize HTML loader."""
        self.extract_links = extract_links

    def load(self, source: str) -> List[Document]:
        """Load HTML document."""
        try:
            logger.info(f"Loading HTML: {source}")
            
            if source.startswith(('http://', 'https://')):
                response = requests.get(source, timeout=30)
                response.raise_for_status()
                html_content = response.text
            else:
                with open(source, 'r', encoding='utf-8') as f:
                    html_content = f.read()

            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            metadata = self.extract_metadata(source, type="html")
            
            # Extract title if available
            if soup.title:
                metadata["title"] = soup.title.string

            # Extract links if requested
            if self.extract_links:
                links = [a.get('href') for a in soup.find_all('a', href=True)]
                metadata["links"] = links

            return [Document(content=text, metadata=metadata)]

        except Exception as e:
            logger.error(f"Error loading HTML {source}: {e}")
            raise


class WebsiteLoader(DocumentLoader):
    """Load documents from websites with crawling capability."""

    def __init__(
        self,
        max_depth: int = 2,
        max_pages: int = 10,
        same_domain_only: bool = True
    ):
        """Initialize website loader."""
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.visited_urls = set()

    def load(self, source: str) -> List[Document]:
        """Load website with optional crawling."""
        try:
            logger.info(f"Loading website: {source}")
            documents = []
            
            # Start with the main page
            self._crawl(source, depth=0, documents=documents)
            
            logger.info(f"Loaded {len(documents)} pages from website")
            return documents

        except Exception as e:
            logger.error(f"Error loading website {source}: {e}")
            raise

    def _crawl(
        self,
        url: str,
        depth: int,
        documents: List[Document]
    ) -> None:
        """Recursively crawl website."""
        if (
            depth > self.max_depth
            or len(documents) >= self.max_pages
            or url in self.visited_urls
        ):
            return

        try:
            self.visited_urls.add(url)
            logger.debug(f"Crawling: {url} (depth={depth})")

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            if text.strip():
                metadata = self.extract_metadata(
                    url,
                    type="website",
                    depth=depth
                )
                
                if soup.title:
                    metadata["title"] = soup.title.string

                documents.append(Document(content=text, metadata=metadata))

            # Extract links for further crawling
            if depth < self.max_depth:
                base_domain = urlparse(url).netloc
                
                for link in soup.find_all('a', href=True):
                    next_url = link.get('href')
                    
                    # Convert relative URLs to absolute
                    if next_url.startswith('/'):
                        parsed = urlparse(url)
                        next_url = f"{parsed.scheme}://{parsed.netloc}{next_url}"
                    elif not next_url.startswith(('http://', 'https://')):
                        continue

                    # Check if same domain
                    if self.same_domain_only:
                        next_domain = urlparse(next_url).netloc
                        if next_domain != base_domain:
                            continue

                    if next_url not in self.visited_urls:
                        self._crawl(next_url, depth + 1, documents)

        except Exception as e:
            logger.warning(f"Error crawling {url}: {e}")


class DocumentLoaderFactory:
    """Factory to create appropriate document loaders."""

    @staticmethod
    def get_loader(source: str, **kwargs) -> DocumentLoader:
        """Get appropriate loader based on source."""
        if source.endswith('.pdf'):
            return PDFLoader()
        elif source.endswith(('.html', '.htm')):
            return HTMLLoader(**kwargs)
        elif source.endswith('.txt'):
            return TextLoader()
        elif source.startswith(('http://', 'https://')):
            # Check if it's a single page or website to crawl
            if kwargs.get('crawl', False):
                return WebsiteLoader(
                    max_depth=kwargs.get('max_depth', 2),
                    max_pages=kwargs.get('max_pages', 10)
                )
            return HTMLLoader(**kwargs)
        else:
            return TextLoader()

