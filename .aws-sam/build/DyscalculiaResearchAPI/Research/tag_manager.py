"""
Tag management system for the Bedrock PDF Analyzer
"""
import os
import json
import boto3
import html
from prompt_templates import TAG_EXPLANATION_PROMPT

class TagManager:
    def __init__(self, output_directory, bedrock_client=None, region='us-east-1'):
        self.output_directory = output_directory
        self.bedrock = bedrock_client or boto3.client('bedrock-runtime', region_name=region)
        self.tags_metadata = self.load_metadata()
    
    def process_tags(self, tags, filename="", research_metadata=None):
        """Process tags, check for duplicates, and explain new ones"""
        if not tags:
            return tags
            
        processed_tags = []
        new_tags = []
        
        for tag in tags:
            tag_lower = tag.lower()
            existing_tag = self._find_existing_tag(tag_lower)
            
            if existing_tag:
                processed_tags.append(existing_tag)
                self._update_existing_tag(existing_tag, filename)
            else:
                processed_tags.append(tag)
                new_tags.append(tag)
                self._create_new_tag(tag, filename)
        
        if new_tags:
            self._explain_new_tags(new_tags, research_metadata)
        
        return processed_tags
    
    def _find_existing_tag(self, tag_lower):
        """Find existing tag (case insensitive)"""
        for existing in self.tags_metadata.keys():
            if existing.lower() == tag_lower:
                return existing
        return None
    
    def _update_existing_tag(self, existing_tag, filename):
        """Update usage count and sources for existing tag"""
        self.tags_metadata[existing_tag]["usage_count"] += 1
        if "sources" not in self.tags_metadata[existing_tag]:
            self.tags_metadata[existing_tag]["sources"] = []
        if filename and filename not in self.tags_metadata[existing_tag]["sources"]:
            self.tags_metadata[existing_tag]["sources"].append(filename)
    
    def _create_new_tag(self, tag, filename):
        """Create new tag entry"""
        self.tags_metadata[tag] = {
            "dyscalculia_relevance": "", 
            "tag_type": "", 
            "research_source": "", 
            "usage_count": 1, 
            "sources": [filename] if filename else []
        }
    
    def _explain_new_tags(self, new_tags, research_metadata=None):
        """Get AI explanation for new tags"""
        tags_str = ", ".join(new_tags)
        research_context = self._build_research_context(research_metadata)
        
        prompt = TAG_EXPLANATION_PROMPT.format(
            tags=tags_str, 
            research_context=research_context
        )
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"max_new_tokens": 1000}
            }
            
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-pro-v1:0',
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content'][0]['text']
            
            self._process_tag_explanations(content, new_tags, research_metadata)
                        
        except Exception as e:
            import logging
            logging.error(f"Error explaining tags: {e}", exc_info=True)
            self._set_default_explanations(new_tags)
    
    def _build_research_context(self, research_metadata):
        """Build research context string for tag explanation"""
        if not research_metadata:
            return ""
        
        authors = research_metadata.get('authors', [])
        last_author = authors[0].split()[-1] if authors else "Unknown"
        year = research_metadata.get('publication_year', 'Unknown')
        title = research_metadata.get('title', 'Unknown')
        return f"\n\nThese tags come from: {last_author}, {year}, {title}"
    
    def _process_tag_explanations(self, content, new_tags, research_metadata):
        """Process AI response for tag explanations"""
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            explanations = json.loads(content[json_start:json_end])
            
            for tag in new_tags:
                if tag in explanations:
                    tag_info = explanations[tag]
                    if isinstance(tag_info, dict):
                        self.tags_metadata[tag]["dyscalculia_relevance"] = html.unescape(
                            tag_info.get("dyscalculia_relevance", "")
                        )
                        self.tags_metadata[tag]["tag_type"] = tag_info.get("tag_type", "")
                    else:
                        self.tags_metadata[tag]["dyscalculia_relevance"] = html.unescape(tag_info)
                    
                    if research_metadata:
                        self.tags_metadata[tag]["research_source"] = self._format_research_source(research_metadata)
    
    def _format_research_source(self, research_metadata):
        """Format research source string"""
        authors = research_metadata.get('authors', [])
        last_author = authors[0].split()[-1] if authors else "Unknown"
        year = research_metadata.get('publication_year', 'Unknown')
        title = research_metadata.get('title', 'Unknown')
        return f"{last_author}, {year}, {title}"
    
    def _set_default_explanations(self, new_tags):
        """Set default explanations for tags when AI fails"""
        for tag in new_tags:
            self.tags_metadata[tag]["dyscalculia_relevance"] = "Relevance to dyscalculia research to be determined"
    
    def load_metadata(self):
        """Load existing tags metadata"""
        tags_file = os.path.join(self.output_directory, "tags_metadata.json")
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_metadata(self):
        """Save tags metadata to JSON and CSV"""
        if not self.tags_metadata:
            return
            
        self._save_json()
        self._save_csv()
    
    def _save_json(self):
        """Save tags metadata as JSON"""
        tags_file = os.path.join(self.output_directory, "tags_metadata.json")
        with open(tags_file, 'w', encoding='utf-8') as f:
            json.dump(self.tags_metadata, f, indent=4, ensure_ascii=False)
        return tags_file
    
    def _save_csv(self):
        """Save tags metadata as CSV"""
        try:
            import pandas as pd
            tags_df = pd.DataFrame([
                {
                    "tag": tag, 
                    "tag_type": info.get("tag_type", ""), 
                    "dyscalculia_relevance": info.get("dyscalculia_relevance", ""), 
                    "research_source": info.get("research_source", ""),
                    "usage_count": info.get("usage_count", 0),
                    "sources": "; ".join(info.get("sources", []))
                }
                for tag, info in self.tags_metadata.items()
            ])
            tags_csv = os.path.join(self.output_directory, "tags_metadata.csv")
            tags_df.to_csv(tags_csv, index=False, encoding='utf-8')
            print(f"Tags metadata saved to: {self._save_json()} and {tags_csv}")
        except (ImportError, PermissionError) as e:
            print(f"Tags metadata saved to: {self._save_json()} (CSV error: {e})")