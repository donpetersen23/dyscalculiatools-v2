import pandas as pd
import json
import os
from PyPDF2 import PdfReader
import re

class ResearchConsolidator:
    def __init__(self, articles_dir, csv_file):
        self.articles_dir = articles_dir
        self.csv_file = csv_file
        self.insights = {
            'definitions': [],
            'causes': [],
            'symptoms': [],
            'assessments': [],
            'interventions': [],
            'outcomes': [],
            'populations': [],
            'key_findings': []
        }
    
    def extract_key_insights(self, text, pmc_id):
        """Extract categorized insights from PDF text"""
        text_lower = text.lower()
        
        # Definition patterns
        if any(term in text_lower for term in ['dyscalculia is', 'defined as', 'mathematical learning disability']):
            definitions = re.findall(r'(?i)(dyscalculia is[^.]{20,200}\.)', text)
            self.insights['definitions'].extend([(pmc_id, d.strip()) for d in definitions[:2]])
        
        # Causes patterns
        cause_patterns = [
            r'(?i)(caused by[^.]{20,150}\.)',
            r'(?i)(etiology[^.]{20,150}\.)',
            r'(?i)(risk factors[^.]{20,150}\.)'
        ]
        for pattern in cause_patterns:
            causes = re.findall(pattern, text)
            self.insights['causes'].extend([(pmc_id, c.strip()) for c in causes[:2]])
        
        # Symptoms patterns
        symptom_patterns = [
            r'(?i)(difficulty with[^.]{20,150}\.)',
            r'(?i)(symptoms include[^.]{20,150}\.)',
            r'(?i)(characterized by[^.]{20,150}\.)'
        ]
        for pattern in symptom_patterns:
            symptoms = re.findall(pattern, text)
            self.insights['symptoms'].extend([(pmc_id, s.strip()) for s in symptoms[:2]])
        
        # Assessment patterns
        assessment_patterns = [
            r'(?i)(assessment[^.]{20,150}\.)',
            r'(?i)(diagnosis[^.]{20,150}\.)',
            r'(?i)(screening[^.]{20,150}\.)'
        ]
        for pattern in assessment_patterns:
            assessments = re.findall(pattern, text)
            self.insights['assessments'].extend([(pmc_id, a.strip()) for a in assessments[:2]])
        
        # Intervention patterns
        intervention_patterns = [
            r'(?i)(intervention[^.]{20,150}\.)',
            r'(?i)(treatment[^.]{20,150}\.)',
            r'(?i)(therapy[^.]{20,150}\.)',
            r'(?i)(training[^.]{20,150}\.)'
        ]
        for pattern in intervention_patterns:
            interventions = re.findall(pattern, text)
            self.insights['interventions'].extend([(pmc_id, i.strip()) for i in interventions[:2]])
        
        # Outcome patterns
        outcome_patterns = [
            r'(?i)(improved[^.]{20,150}\.)',
            r'(?i)(significant[^.]{20,150}\.)',
            r'(?i)(effective[^.]{20,150}\.)',
            r'(?i)(results showed[^.]{20,150}\.)'
        ]
        for pattern in outcome_patterns:
            outcomes = re.findall(pattern, text)
            self.insights['outcomes'].extend([(pmc_id, o.strip()) for o in outcomes[:2]])
    
    def process_high_relevance_papers(self):
        """Process papers with highest relevance scores"""
        df = pd.read_csv(self.csv_file)
        top_papers = df.nlargest(15, 'Relevance_Score')
        
        for _, row in top_papers.iterrows():
            pmc_id = row['PMC_ID']
            pdf_path = os.path.join(self.articles_dir, f"{pmc_id}.pdf")
            
            if os.path.exists(pdf_path):
                try:
                    with open(pdf_path, 'rb') as file:
                        reader = PdfReader(file)
                        text = ""
                        for page in reader.pages[:10]:  # First 10 pages
                            text += page.extract_text()
                        
                        self.extract_key_insights(text, pmc_id)
                        
                        # Add key findings from CSV
                        if pd.notna(row['Abstract_Preview']):
                            self.insights['key_findings'].append((pmc_id, row['Abstract_Preview']))
                            
                except Exception as e:
                    print(f"Error processing {pmc_id}: {e}")
    
    def generate_consolidated_report(self):
        """Generate consolidated research insights"""
        report = []
        report.append("=" * 80)
        report.append("CONSOLIDATED DYSCALCULIA RESEARCH INSIGHTS")
        report.append("=" * 80)
        
        # Definitions
        if self.insights['definitions']:
            report.append("\n🔍 DEFINITIONS & CHARACTERISTICS:")
            report.append("-" * 50)
            for pmc_id, definition in self.insights['definitions'][:5]:
                report.append(f"• {definition} (Source: {pmc_id})")
        
        # Causes
        if self.insights['causes']:
            report.append("\n🧬 CAUSES & RISK FACTORS:")
            report.append("-" * 50)
            for pmc_id, cause in self.insights['causes'][:5]:
                report.append(f"• {cause} (Source: {pmc_id})")
        
        # Symptoms
        if self.insights['symptoms']:
            report.append("\n⚠️ SYMPTOMS & MANIFESTATIONS:")
            report.append("-" * 50)
            for pmc_id, symptom in self.insights['symptoms'][:5]:
                report.append(f"• {symptom} (Source: {pmc_id})")
        
        # Assessments
        if self.insights['assessments']:
            report.append("\n📋 ASSESSMENT & DIAGNOSIS:")
            report.append("-" * 50)
            for pmc_id, assessment in self.insights['assessments'][:5]:
                report.append(f"• {assessment} (Source: {pmc_id})")
        
        # Interventions
        if self.insights['interventions']:
            report.append("\n🎯 INTERVENTIONS & TREATMENTS:")
            report.append("-" * 50)
            for pmc_id, intervention in self.insights['interventions'][:8]:
                report.append(f"• {intervention} (Source: {pmc_id})")
        
        # Outcomes
        if self.insights['outcomes']:
            report.append("\n📈 RESEARCH OUTCOMES:")
            report.append("-" * 50)
            for pmc_id, outcome in self.insights['outcomes'][:6]:
                report.append(f"• {outcome} (Source: {pmc_id})")
        
        # Key findings
        if self.insights['key_findings']:
            report.append("\n💡 KEY RESEARCH FINDINGS:")
            report.append("-" * 50)
            for pmc_id, finding in self.insights['key_findings'][:8]:
                report.append(f"• {finding[:200]}... (Source: {pmc_id})")
        
        return "\n".join(report)
    
    def save_insights(self, output_file="consolidated_insights.txt"):
        """Save consolidated insights to file"""
        report = self.generate_consolidated_report()
        output_path = os.path.join(os.path.dirname(self.csv_file), output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Consolidated insights saved to: {output_path}")
        return report

if __name__ == "__main__":
    articles_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    csv_file = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\dyscalculia_relevance_scores.csv"
    
    consolidator = ResearchConsolidator(articles_dir, csv_file)
    
    print("Processing high-relevance research papers...")
    consolidator.process_high_relevance_papers()
    
    print("Generating consolidated insights...")
    report = consolidator.save_insights()
    
    print("\n" + report)