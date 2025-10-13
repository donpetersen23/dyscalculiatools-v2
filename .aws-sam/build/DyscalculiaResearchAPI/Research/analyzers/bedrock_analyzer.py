import json
import boto3
import html

class BedrockAnalyzer:
    """Handles AWS Bedrock AI analysis"""
    
    def __init__(self, region='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        # Nova Pro pricing (input, output per 1K tokens)
        self.input_price = 0.0008
        self.output_price = 0.004
    
    def analyze_text(self, text, sections_found, filename):
        """Use Bedrock to extract metadata and generate summary"""
        prompt = f"""Analyze this research article and extract the following information in JSON format:

1. authors: List of author names (array of strings)
2. publication_year: Year of publication (integer)
3. title: Article title (string)
4. relevance_score: Rate 0-10 how relevant this study is to dyscalculia/math learning disabilities:
   - 10: Directly studies dyscalculia or math learning disabilities
   - 7-9: Studies math education, number sense, or arithmetic interventions
   - 4-6: Studies general learning disabilities, cognitive development, or educational methods
   - 1-3: Tangentially related (brain function, child development, but not math-specific)
   - 0: Not related to learning or education
5. research_category: Classify as:
   - "direct" if it contributes to understanding or addressing dyscalculia, including studies of dyscalculia, math education interventions, cognitive interventions for learning disabilities, research discussing dyscalculia in any context, or foundational cognitive science relevant to math learning
   - "supportive" if it is not directly about dyscalculia but provides useful context, such as general education strategies, cognitive psychology, neuroscience of learning, or studies on other learning disabilities that might inform dyscalculia research

For items 6-12 below, write in a friendly, conversational tone - like you're explaining to a parent or teacher over coffee. Use simple, everyday language.

6. summary: 3-5 sentences in conversational, everyday terms that explain:
   - What specific findings, methods, or insights from this research are relevant to understanding dyscalculia or math learning difficulties
   - If the study identifies research gaps, trends, or comparisons (e.g., which conditions are under-researched vs well-studied), mention these
   - How practitioners, researchers, or individuals with dyscalculia could use or benefit from this knowledge
   - Focus on extracting concrete information rather than general statements about potential relevance.

For items 7-10 below, only provide information if the research is direct research related to dyscalculia. If not, respond with "n/a" as appropriate.
   
7. one_on_one_applicability: 1-2 sentences with specific, actionable strategies for parents/tutors using everyday materials (or "n/a" if supportive)
8. small_group_applicability: 1-2 sentences with concrete methods for special education teachers (or "n/a" if supportive)
9. large_group_applicability: 1-2 sentences with practical adaptations for general education teachers (or "n/a" if supportive)
10. self_education_applicability: 1-2 sentences on how individuals with dyscalculia can use this to improve their own math skills (or "n/a" if supportive)
11. doi: DOI number, journal URL, or publication link if available (or 'Not found' if none)
12. tags: 4-6 specific tags that capture the key aspects of this research that have either a direct or supportive relationship with dyscalculia. Use the most appropriate terminology - scientific when necessary (e.g., "parietal cortex", "working memory") but accessible when possible (e.g., "times tables" rather than "multiplication automaticity")

Article text:
{text[:8000]}

Respond ONLY with valid JSON in this exact format:
{{
  "authors": ["Author Name"],
  "publication_year": 2024,
  "title": "Article Title",
  "relevance_score": 8,
  "research_category": "direct",
  "summary": "Conversational summary combining what the research reveals, what specific math skills are addressed, how it helps children with dyscalculia, and practical benefits.",
  "one_on_one_applicability": "Specific strategies parents and tutors can use with everyday materials.",
  "small_group_applicability": "Concrete methods special education teachers can use.",
  "large_group_applicability": "Practical ways general education teachers can adapt this for their classrooms.",
  "self_education_applicability": "How adults with dyscalculia can use this to improve their own math skills.",
  "doi": "DOI number, journal URL, or publication link if available (or 'Not found' if none)",
  "tags": ["3-5 relevant topic tags"]
}}"""

        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"max_new_tokens": 2000}
            }
            
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-pro-v1:0',
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content'][0]['text']
            
            # Get token usage
            input_tokens = result['usage']['inputTokens']
            output_tokens = result['usage']['outputTokens']
            cost = (input_tokens / 1000 * self.input_price) + (output_tokens / 1000 * self.output_price)
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                metadata = json.loads(content[json_start:json_end])
                
                # Decode HTML entities
                for key, value in metadata.items():
                    if key != 'tags':  # Tags handled by TagsManager
                        metadata[key] = self._decode_html_entities(value)
                
                metadata['_input_tokens'] = input_tokens
                metadata['_output_tokens'] = output_tokens
                metadata['_estimated_cost'] = round(cost, 6)
                metadata['_sections_analyzed'] = sections_found
                return metadata
                
        except Exception as e:
            print(f"Bedrock error for {filename}: {e}")
        
        return None
    
    def _decode_html_entities(self, data):
        """Decode HTML entities in strings and lists"""
        if isinstance(data, str):
            return html.unescape(data)
        elif isinstance(data, list):
            return [html.unescape(v) if isinstance(v, str) else v for v in data]
        return data