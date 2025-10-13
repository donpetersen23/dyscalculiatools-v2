import os
import json
import boto3
from datetime import datetime

class TagEnhancer:
    def __init__(self, research_dir, output_dir=None, region='us-east-1'):
        self.research_dir = research_dir
        self.output_dir = output_dir or research_dir
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        self.input_price = 0.0025
        self.output_price = 0.0125
        
    def load_metadata(self):
        """Load research metadata and tags metadata"""
        research_file = os.path.join(self.output_dir, "research_metadata.json")
        tags_file = os.path.join(self.output_dir, "tags_metadata.json")
        
        with open(research_file, 'r', encoding='utf-8') as f:
            research_data = json.load(f)
        
        with open(tags_file, 'r', encoding='utf-8') as f:
            tags_data = json.load(f)
            
        return research_data, tags_data
    
    def get_articles_for_tag(self, tag, research_data, tags_data):
        """Get all articles that use a specific tag"""
        tag_info = tags_data.get(tag, {})
        sources = tag_info.get("sources", [])
        
        articles = []
        for article in research_data:
            if article.get('filename') in sources:
                articles.append({
                    'title': article.get('title', 'Unknown'),
                    'authors': article.get('authors', []),
                    'year': article.get('publication_year', 'Unknown'),
                    'summary': article.get('summary', ''),
                    'relevance_score': article.get('relevance_score', 0)
                })
        
        return articles
    
    def enhance_tag_definition(self, tag, articles, current_definition):
        """Generate enhanced definition based on all articles using this tag"""
        
        articles_context = "\n\n".join([
            f"Article {i+1}: {a['title']} ({a['year']})\n"
            f"Authors: {', '.join(a['authors'])}\n"
            f"Relevance: {a['relevance_score']}/10\n"
            f"Summary: {a['summary']}"
            for i, a in enumerate(articles[:10])  # Limit to 10 articles to avoid token limits
        ])
        
        prompt = f"""Based on multiple research articles, create a comprehensive definition for this tag in dyscalculia research.

Tag: {tag}

Current definition: {current_definition if current_definition else "None"}

Articles using this tag ({len(articles)} total, showing up to 10):
{articles_context}

Create an enhanced definition that:
1. Synthesizes insights from all these articles
2. Explains the tag's relevance to dyscalculia research
3. Notes any patterns, trends, or key findings across studies
4. Remains concise (2-4 sentences)

Respond ONLY with JSON:
{{
  "enhanced_definition": "Your comprehensive definition here",
  "key_insights": "Brief note on patterns or trends across studies"
}}"""

        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"max_new_tokens": 500}
            }
            
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-premier-v1:0',
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content'][0]['text']
            
            # Get token usage
            input_tokens = result['usage']['inputTokens']
            output_tokens = result['usage']['outputTokens']
            cost = (input_tokens / 1000 * self.input_price) + (output_tokens / 1000 * self.output_price)
            
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                enhancement = json.loads(content[json_start:json_end])
                return enhancement, cost
                
        except Exception as e:
            print(f"Error enhancing tag '{tag}': {e}")
            return None, 0
    
    def enhance_all_tags(self, min_usage=2):
        """Enhance definitions for all tags used by multiple articles"""
        research_data, tags_data = self.load_metadata()
        
        # Filter tags by minimum usage
        tags_to_enhance = {
            tag: info for tag, info in tags_data.items() 
            if info.get('usage_count', 0) >= min_usage
        }
        
        print(f"Found {len(tags_to_enhance)} tags used by {min_usage}+ articles")
        print(f"Processing enhancements...\n")
        
        enhanced_tags = {}
        total_cost = 0
        
        for i, (tag, info) in enumerate(tags_to_enhance.items(), 1):
            usage = info.get('usage_count', 0)
            current_def = info.get('dyscalculia_relevance', '')
            
            print(f"[{i}/{len(tags_to_enhance)}] Enhancing '{tag}' (used by {usage} articles)...")
            
            articles = self.get_articles_for_tag(tag, research_data, tags_data)
            enhancement, cost = self.enhance_tag_definition(tag, articles, current_def)
            
            if enhancement:
                enhanced_tags[tag] = {
                    **info,
                    'dyscalculia_relevance': enhancement.get('enhanced_definition', current_def),
                    'key_insights': enhancement.get('key_insights', ''),
                    'enhanced_date': datetime.now().isoformat(),
                    'articles_analyzed': len(articles)
                }
                total_cost += cost
                print(f"  ✓ Enhanced (cost: ${cost:.6f})")
            else:
                enhanced_tags[tag] = info
                print(f"  ✗ Failed to enhance")
        
        # Merge with tags that weren't enhanced
        for tag, info in tags_data.items():
            if tag not in enhanced_tags:
                enhanced_tags[tag] = info
        
        # Save enhanced tags with version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup original
        backup_file = os.path.join(self.output_dir, f"tags_metadata_backup_{timestamp}.json")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, indent=4, ensure_ascii=False)
        
        # Save enhanced version
        enhanced_file = os.path.join(self.output_dir, "tags_metadata.json")
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_tags, f, indent=4, ensure_ascii=False)
        
        # Save CSV
        import pandas as pd
        tags_df = pd.DataFrame([
            {
                "tag": tag,
                "tag_type": info.get("tag_type", ""),
                "dyscalculia_relevance": info.get("dyscalculia_relevance", ""),
                "key_insights": info.get("key_insights", ""),
                "research_source": info.get("research_source", ""),
                "usage_count": info.get("usage_count", 0),
                "sources": "; ".join(info.get("sources", [])),
                "enhanced_date": info.get("enhanced_date", "")
            }
            for tag, info in enhanced_tags.items()
        ])
        
        csv_file = os.path.join(self.output_dir, "tags_metadata.csv")
        try:
            tags_df.to_csv(csv_file, index=False, encoding='utf-8')
        except PermissionError:
            print("\nWarning: Could not save CSV (file may be open)")
        
        print(f"\n{'='*80}")
        print(f"Enhancement Summary:")
        print(f"  Tags enhanced: {len(tags_to_enhance)}")
        print(f"  Total cost: ${total_cost:.6f}")
        print(f"  Backup saved: {backup_file}")
        print(f"  Enhanced tags saved: {enhanced_file}")
        print(f"{'='*80}")

def main():
    """Run tag enhancement"""
    research_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research"
    
    enhancer = TagEnhancer(research_dir)
    
    # Enhance tags used by 2 or more articles
    enhancer.enhance_all_tags(min_usage=2)

if __name__ == "__main__":
    main()
