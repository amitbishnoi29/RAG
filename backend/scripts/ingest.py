#!/usr/bin/env python3
"""
Document ingestion script for RAG Chatbot
Usage: python scripts/ingest.py <file_path> [--file-type <type>]
"""

import argparse
import sys
import os
import asyncio
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.document_service import document_service
from services.weaviate_client import weaviate_client
from app.config import settings


def ingest_file(file_path: str, file_type: str = None):
    """Ingest a single file"""
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist")
            return False
        
        print(f"Ingesting file: {file_path}")
        
        if file_type is None:
            file_type = os.path.splitext(file_path)[1]
        
        result = document_service.ingest_document(file_path)
        
        if result["success"]:
            print(f"✅ Successfully ingested: {result['filename']}")
            print(f"   Created {result['chunks_created']} chunks")
            print(f"   File size: {result['file_size']} bytes")
            return True
        else:
            print(f"❌ Failed to ingest: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error ingesting file: {e}")
        return False


def ingest_directory(directory_path: str, recursive: bool = False):
    """Ingest all supported files in a directory"""
    try:
        directory = Path(directory_path)
        if not directory.exists():
            print(f"Error: Directory '{directory_path}' does not exist")
            return False
        
        pattern = "**/*" if recursive else "*"
        supported_extensions = settings.allowed_file_types
        
        files_to_ingest = []
        for ext in supported_extensions:
            files_to_ingest.extend(directory.glob(f"{pattern}{ext}"))
        
        if not files_to_ingest:
            print(f"No supported files found in {directory_path}")
            print(f"Supported extensions: {supported_extensions}")
            return False
        
        print(f"Found {len(files_to_ingest)} files to ingest")
        
        success_count = 0
        for file_path in files_to_ingest:
            if ingest_file(str(file_path)):
                success_count += 1
        
        print(f"\n📊 Summary: {success_count}/{len(files_to_ingest)} files ingested successfully")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error ingesting directory: {e}")
        return False


def ingest_text(text_content: str, filename: str = "manual_input"):
    """Ingest raw text content"""
    try:
        print(f"Ingesting text content as: {filename}")
        
        result = document_service.ingest_text_content(text_content, filename)
        
        if result["success"]:
            print(f"✅ Successfully ingested text: {result['filename']}")
            print(f"   Created {result['chunks_created']} chunks")
            return True
        else:
            print(f"❌ Failed to ingest text: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error ingesting text: {e}")
        return False


def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    try:
        print("Clearing all documents from knowledge base...")
        weaviate_client.delete_all_documents()
        print("✅ Knowledge base cleared successfully")
        return True
    except Exception as e:
        print(f"❌ Error clearing knowledge base: {e}")
        return False


def show_stats():
    """Show knowledge base statistics"""
    try:
        count = weaviate_client.get_document_count()
        print(f"📊 Knowledge Base Statistics:")
        print(f"   Total document chunks: {count}")
        return True
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into RAG knowledge base")
    parser.add_argument("path", nargs="?", help="File or directory path to ingest")
    parser.add_argument("--text", help="Ingest raw text content")
    parser.add_argument("--filename", help="Filename for text content (when using --text)")
    parser.add_argument("--directory", action="store_true", help="Treat path as directory")
    parser.add_argument("--recursive", action="store_true", help="Recursively ingest directory")
    parser.add_argument("--clear", action="store_true", help="Clear all documents from knowledge base")
    parser.add_argument("--stats", action="store_true", help="Show knowledge base statistics")
    parser.add_argument("--file-type", help="Override file type detection")
    
    args = parser.parse_args()
    
    if args.clear:
        clear_knowledge_base()
        return
    
    if args.stats:
        show_stats()
        return
    
    if args.text:
        filename = args.filename or "manual_input"
        ingest_text(args.text, filename)
        return
    
    if not args.path:
        parser.print_help()
        return
    
    if args.directory or os.path.isdir(args.path):
        ingest_directory(args.path, args.recursive)
    else:
        ingest_file(args.path, args.file_type)
    
    # Show stats after ingestion
    show_stats()


if __name__ == "__main__":
    main() 