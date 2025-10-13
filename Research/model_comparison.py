import os
import json
import boto3
import PyPDF2
import pandas as pd
import time

class ModelComparison:
    def __init__(self, pdf_directory, output_directory, region='us-east-1'):
        self.pdf_directory = pdf_directory
        self.output_directory = output_directory
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        
        # Models to test (only those with "Access granted" for text)
        self.models = {
            'Nova Premier': 'us.amazon.nova-premier-v1:0',
            'Nova Pro': 'amazon.nova-pro-v1:0', 
            'Nova Lite': 'amazon.nova-lite-v1:0',
            'Nova Micro': 'amazon.nova-micro-v1:0',
            'Claude Sonnet 4': 'us.anthropic.claude-sonnet-4-20250514-v1:0',
            'Claude 3 Haiku': 'anthropic.claude-3-haiku-20240307-v1:0'
        }
        
        # Pricing per 1K tokens (input, output)
        self.pricing = {
            'Nova Premier': (0.0025, 0.0125),
            'Nova Pro': (0.0008, 0.0032),
            'Nova Lite': (0.00006, 0.00024),
            'Nova Micro': (0.000035, 0.00014),
            'Claude Sonnet 4': (0.003, 0.015),
            'Claude 3 Haiku': (0.00025, 0.00125)
        }
        
        self.results = []
        
    def extract_text_from_pdf(self, pdf_path, max_pages=10):
        """Extract text from PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return "".join(page.extract_text() + "\n" for page in reader.pages[:max_pages])
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
            return ""
    
    def _build_result(self, model_name, model_id, processing_time, success=False, error=None, metadata=None, input_tokens=0, output_tokens=0):
        """Helper to build result dictionary"""
        result = {
            'model_name': model_name,
            'model_id': model_id,
            'processing_time': round(processing_time, 2),
            'success': success,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }
        
        # Calculate cost
        if model_name in self.pricing:
            input_price, output_price = self.pricing[model_name]
            cost = (input_tokens / 1000 * input_price) + (output_tokens / 1000 * output_price)
            result['estimated_cost'] = round(cost, 6)
        
        if error:
            result['error'] = error
        if metadata:
            result.update(metadata)
        return result
    
    def get_prompt(self, text):
        """Get the standard prompt"""
        return f"""Analyze this research article and extract the following information in JSON format:

1. authors: List of author names (array of strings)
2. publication_year: Year of publication (integer)
3. title: Article title (string)
4. dyscalculia_relevance: Write a concise, practical explanation (2-3 sentences) in everyday language:
   - What specific math skills children with dyscalculia struggle with are addressed here
   - How the research approach or findings could help children with math learning differences
   - What practical benefits exist for students, parents, or teachers
5. summary: Write a clear, conversational summary (2-3 sentences) in everyday terms:
   - What the researchers wanted to find out (avoid technical research terms)
   - Who participated and what they did (use simple, human language)
   - What the results showed and why it matters (focus on real-world impact)
6. one_on_one_applicability: Specific, actionable strategies for parents/tutors using age-appropriate materials and methods (1-2 sentences)
7. study_limitations: Key limitations that affect interpretation and generalizability (1-2 sentences)

Article text:
{text[:8000]}

Respond ONLY with valid JSON in this exact format:
{{
  "authors": ["Author Name"],
  "publication_year": 2024,
  "title": "Article Title",
  "dyscalculia_relevance": "Practical explanation in everyday language of how this helps children with dyscalculia and their families.",
  "summary": "Conversational summary explaining what researchers wanted to know, what they did, and what they found in simple terms.",
  "one_on_one_applicability": "Specific, actionable strategies using age-appropriate materials and methods.",
  "study_limitations": "Key limitations affecting interpretation and generalizability of findings."
}}"""

    def test_model(self, model_name, model_id, text):
        """Test a single model"""
        print(f"Testing {model_name}...")
        start_time = time.time()
        input_tokens = 0
        output_tokens = 0
        
        try:
            prompt = self.get_prompt(text)
            
            # Handle different API formats
            if 'claude' in model_id.lower():
                response = self.bedrock.converse(
                    modelId=model_id,
                    messages=[{"role": "user", "content": [{"text": prompt}]}],
                    inferenceConfig={"maxTokens": 2000}
                )
                content = response['output']['message']['content'][0]['text']
                input_tokens = response['usage']['inputTokens']
                output_tokens = response['usage']['outputTokens']
            elif 'nova' in model_id.lower():
                response = self.bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "messages": [{"role": "user", "content": [{"text": prompt}]}],
                        "inferenceConfig": {"max_new_tokens": 2000}
                    })
                )
                result = json.loads(response['body'].read())
                content = result['output']['message']['content'][0]['text']
                input_tokens = result['usage']['inputTokens']
                output_tokens = result['usage']['outputTokens']
            else:  # Titan
                response = self.bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "inputText": prompt,
                        "textGenerationConfig": {"maxTokenCount": 2000, "temperature": 0.7}
                    })
                )
                result = json.loads(response['body'].read())
                content = result['results'][0]['outputText']
                input_tokens = result.get('inputTextTokenCount', 0)
                output_tokens = result['results'][0].get('tokenCount', 0)
            
            # Extract and parse JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end <= json_start:
                return self._build_result(model_name, model_id, time.time() - start_time, 
                                         error=f'No JSON found. Response: {content[:200]}',
                                         input_tokens=input_tokens, output_tokens=output_tokens)
            
            metadata = json.loads(content[json_start:json_end])
            return self._build_result(model_name, model_id, time.time() - start_time, 
                                     success=True, metadata=metadata,
                                     input_tokens=input_tokens, output_tokens=output_tokens)
                
        except json.JSONDecodeError:
            return self._build_result(model_name, model_id, time.time() - start_time,
                                     error=f'JSON parse error. Response: {content[:200]}',
                                     input_tokens=input_tokens, output_tokens=output_tokens)
        except Exception as e:
            return self._build_result(model_name, model_id, time.time() - start_time, error=str(e),
                                     input_tokens=input_tokens, output_tokens=output_tokens)
    
    def run_comparison(self, pdf_filename):
        """Run comparison on a single PDF"""
        pdf_path = os.path.join(self.pdf_directory, pdf_filename)
        
        if not os.path.exists(pdf_path):
            print(f"PDF not found: {pdf_path}")
            return
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print("No text extracted from PDF")
            return
        
        print(f"Testing {len(self.models)} models on {pdf_filename}...")
        
        for model_name, model_id in self.models.items():
            result = self.test_model(model_name, model_id, text)
            result['pdf_filename'] = pdf_filename
            self.results.append(result)
            time.sleep(1)
        
        self.save_results()
        self.generate_comparison_report()
    
    def save_results(self):
        """Save results to JSON and CSV"""
        json_path = os.path.join(self.output_directory, "model_comparison.json")
        csv_path = os.path.join(self.output_directory, "model_comparison.csv")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)
        print(f"Results saved to {json_path}")
        
        if self.results:
            try:
                pd.DataFrame(self.results).to_csv(csv_path, index=False, encoding='utf-8')
                print(f"Results saved to {csv_path}")
            except PermissionError:
                print(f"Warning: Could not save CSV (file may be open in another program). JSON saved successfully.")
    
    def generate_comparison_report(self):
        """Generate comparison report"""
        if not self.results:
            return
        
        print("\n" + "="*80)
        print("MODEL COMPARISON REPORT")
        print("="*80)
        
        successful = [r for r in self.results if r.get('success')]
        failed = [r for r in self.results if not r.get('success')]
        
        print(f"\nSuccessful: {len(successful)}/{len(self.results)} models")
        
        if successful:
            print("\nProcessing Times (fastest to slowest):")
            for r in sorted(successful, key=lambda x: x['processing_time']):
                cost = f"${r.get('estimated_cost', 0):.6f}" if 'estimated_cost' in r else "N/A"
                print(f"  {r['model_name']}: {r['processing_time']}s (Cost: {cost})")
        
        if failed:
            print("\nFailed Models:")
            for r in failed:
                print(f"  {r['model_name']}: {r.get('error', 'Unknown error')}")
        
        if successful:
            print("\nCost Comparison (cheapest to most expensive):")
            for r in sorted(successful, key=lambda x: x.get('estimated_cost', 0)):
                cost = f"${r.get('estimated_cost', 0):.6f}"
                print(f"  {r['model_name']}: {cost}")
        
        total_cost = sum(r.get('estimated_cost', 0) for r in successful)
        print(f"\nTotal estimated cost: ${total_cost:.6f}")
        print("\nDetailed results saved to output files")

if __name__ == "__main__":
    articles_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    output_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research"
    
    # Test with the first PDF (bryant_2014.pdf)
    test_pdf = "bryant_2014.pdf"
    
    comparison = ModelComparison(articles_dir, output_dir)
    comparison.run_comparison(test_pdf)