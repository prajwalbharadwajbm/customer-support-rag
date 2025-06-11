#!/usr/bin/env python3
"""
Document analyzer utility to inspect and analyze documents before vectorization.
Helps understand the content and structure of PDF and DOCX files.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    def __init__(self):
        """Initialize the document analyzer."""
        self.supported_extensions = {'.pdf', '.docx'}
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def get_file_type(self, file_path: str) -> Optional[str]:
        """Determine the file type from the file extension."""
        file_ext = Path(file_path).suffix.lower()
        if file_ext in self.supported_extensions:
            return file_ext[1:]  # Remove the dot
        return None
    
    def analyze_pdf(self, file_path: str) -> Dict:
        """Analyze a PDF file and return statistics."""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            total_text = ""
            page_lengths = []
            
            for doc in documents:
                page_text = doc.page_content
                total_text += page_text + "\n"
                page_lengths.append(len(page_text))
            
            # Split into chunks to see how many chunks would be created
            chunks = self.text_splitter.split_text(total_text)
            
            stats = {
                'file_type': 'PDF',
                'file_path': file_path,
                'file_size_bytes': os.path.getsize(file_path),
                'total_pages': len(documents),
                'total_characters': len(total_text),
                'total_words': len(total_text.split()),
                'average_page_length': sum(page_lengths) / len(page_lengths) if page_lengths else 0,
                'min_page_length': min(page_lengths) if page_lengths else 0,
                'max_page_length': max(page_lengths) if page_lengths else 0,
                'estimated_chunks': len(chunks),
                'pages_info': [
                    {
                        'page_number': i + 1,
                        'character_count': length,
                        'word_count': len(documents[i].page_content.split())
                    }
                    for i, length in enumerate(page_lengths)
                ]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to analyze PDF {file_path}: {str(e)}")
            return {'error': str(e)}
    
    def analyze_docx(self, file_path: str) -> Dict:
        """Analyze a DOCX file and return statistics."""
        try:
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            
            # DOCX typically loads as a single document
            doc = documents[0] if documents else None
            if not doc:
                return {'error': 'No content found in DOCX file'}
            
            total_text = doc.page_content
            
            # Split into chunks to see how many chunks would be created
            chunks = self.text_splitter.split_text(total_text)
            
            # Count paragraphs (rough estimate)
            paragraphs = [p.strip() for p in total_text.split('\n\n') if p.strip()]
            
            stats = {
                'file_type': 'DOCX',
                'file_path': file_path,
                'file_size_bytes': os.path.getsize(file_path),
                'total_characters': len(total_text),
                'total_words': len(total_text.split()),
                'estimated_paragraphs': len(paragraphs),
                'estimated_chunks': len(chunks),
                'average_paragraph_length': sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
                'content_preview': total_text[:500] + "..." if len(total_text) > 500 else total_text
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to analyze DOCX {file_path}: {str(e)}")
            return {'error': str(e)}
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single file and return statistics."""
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        file_type = self.get_file_type(file_path)
        
        if file_type == 'pdf':
            return self.analyze_pdf(file_path)
        elif file_type == 'docx':
            return self.analyze_docx(file_path)
        else:
            return {'error': f'Unsupported file type: {file_path}'}
    
    def analyze_directory(self, directory_path: str) -> Dict:
        """Analyze all supported files in a directory."""
        if not os.path.exists(directory_path):
            return {'error': f'Directory not found: {directory_path}'}
        
        results = {
            'directory': directory_path,
            'summary': {'pdf': [], 'docx': []},
            'total_stats': {
                'total_files': 0,
                'total_size_bytes': 0,
                'total_characters': 0,
                'total_words': 0,
                'total_estimated_chunks': 0
            }
        }
        
        # Find all supported files
        for ext in self.supported_extensions:
            pattern = f"**/*{ext}"
            files = list(Path(directory_path).glob(pattern))
            
            for file_path in files:
                print(f"Analyzing {file_path}...")
                stats = self.analyze_file(str(file_path))
                
                if 'error' not in stats:
                    file_type = stats['file_type'].lower()
                    results['summary'][file_type].append(stats)
                    
                    # Update totals
                    results['total_stats']['total_files'] += 1
                    results['total_stats']['total_size_bytes'] += stats.get('file_size_bytes', 0)
                    results['total_stats']['total_characters'] += stats.get('total_characters', 0)
                    results['total_stats']['total_words'] += stats.get('total_words', 0)
                    results['total_stats']['total_estimated_chunks'] += stats.get('estimated_chunks', 0)
        
        return results
    
    def print_file_stats(self, stats: Dict):
        """Print formatted statistics for a single file."""
        if 'error' in stats:
            print(f"❌ Error: {stats['error']}")
            return
        
        print(f"\n📄 {stats['file_type']} File Analysis")
        print(f"📁 Path: {stats['file_path']}")
        print(f"💾 Size: {stats['file_size_bytes']:,} bytes ({stats['file_size_bytes']/1024:.1f} KB)")
        print(f"📝 Characters: {stats['total_characters']:,}")
        print(f"🔤 Words: {stats['total_words']:,}")
        print(f"🧩 Estimated Chunks: {stats['estimated_chunks']}")
        
        if stats['file_type'] == 'PDF':
            print(f"📑 Pages: {stats['total_pages']}")
            print(f"📊 Avg Page Length: {stats['average_page_length']:.0f} characters")
            print(f"📈 Min/Max Page Length: {stats['min_page_length']}/{stats['max_page_length']} characters")
            
            if len(stats['pages_info']) <= 5:
                print("\n📋 Page Details:")
                for page in stats['pages_info']:
                    print(f"  Page {page['page_number']}: {page['character_count']} chars, {page['word_count']} words")
        
        elif stats['file_type'] == 'DOCX':
            print(f"📋 Estimated Paragraphs: {stats['estimated_paragraphs']}")
            print(f"📊 Avg Paragraph Length: {stats['average_paragraph_length']:.0f} characters")
            
            if 'content_preview' in stats:
                print(f"\n👀 Content Preview:")
                print(f"   {stats['content_preview']}")
    
    def print_directory_stats(self, results: Dict):
        """Print formatted statistics for a directory analysis."""
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return
        
        print(f"\n📂 Directory Analysis: {results['directory']}")
        print("=" * 60)
        
        # Summary statistics
        totals = results['total_stats']
        print(f"📊 Summary Statistics:")
        print(f"   Total Files: {totals['total_files']}")
        print(f"   Total Size: {totals['total_size_bytes']:,} bytes ({totals['total_size_bytes']/1024/1024:.1f} MB)")
        print(f"   Total Characters: {totals['total_characters']:,}")
        print(f"   Total Words: {totals['total_words']:,}")
        print(f"   Estimated Total Chunks: {totals['total_estimated_chunks']}")
        
        # File type breakdown
        pdf_count = len(results['summary']['pdf'])
        docx_count = len(results['summary']['docx'])
        
        print(f"\n📋 File Type Breakdown:")
        print(f"   PDF Files: {pdf_count}")
        print(f"   DOCX Files: {docx_count}")
        
        if pdf_count > 0:
            pdf_stats = results['summary']['pdf']
            total_pages = sum(stats['total_pages'] for stats in pdf_stats)
            avg_pages = total_pages / pdf_count
            print(f"   Total PDF Pages: {total_pages}")
            print(f"   Average Pages per PDF: {avg_pages:.1f}")
        
        if docx_count > 0:
            docx_stats = results['summary']['docx']
            total_paragraphs = sum(stats.get('estimated_paragraphs', 0) for stats in docx_stats)
            avg_paragraphs = total_paragraphs / docx_count if docx_count > 0 else 0
            print(f"   Total DOCX Paragraphs: {total_paragraphs}")
            print(f"   Average Paragraphs per DOCX: {avg_paragraphs:.1f}")
        
        # Individual file details (if not too many)
        all_files = results['summary']['pdf'] + results['summary']['docx']
        if len(all_files) <= 10:
            print(f"\n📄 Individual File Details:")
            for stats in all_files:
                file_name = Path(stats['file_path']).name
                print(f"   {file_name} ({stats['file_type']}): {stats['total_words']:,} words, {stats['estimated_chunks']} chunks")

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze PDF and DOCX documents before vectorization")
    parser.add_argument("--file", "-f", type=str, help="Path to a single document file")
    parser.add_argument("--directory", "-d", type=str, help="Path to directory containing documents")
    
    args = parser.parse_args()
    
    if not args.file and not args.directory:
        parser.print_help()
        print("\nError: You must specify either --file or --directory")
        sys.exit(1)
    
    analyzer = DocumentAnalyzer()
    
    try:
        if args.file:
            # Analyze single file
            print("🔍 Analyzing single file...")
            stats = analyzer.analyze_file(args.file)
            analyzer.print_file_stats(stats)
            
        elif args.directory:
            # Analyze directory
            print(f"🔍 Analyzing directory: {args.directory}")
            results = analyzer.analyze_directory(args.directory)
            analyzer.print_directory_stats(results)
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 