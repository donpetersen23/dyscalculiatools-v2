"""
Dyscalculia Research Analysis Package

Modular components for analyzing research papers with AWS Bedrock.
"""

from .pdf_extractor import PDFExtractor
from .bedrock_analyzer import BedrockAnalyzer
from .tags_manager import TagsManager
from .report_generator import ReportGenerator
from .batch_processor import BatchProcessor

__all__ = ['PDFExtractor', 'BedrockAnalyzer', 'TagsManager', 'ReportGenerator', 'BatchProcessor']