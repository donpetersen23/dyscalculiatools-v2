"""
Prompt templates for the Bedrock PDF Analyzer
"""

ANALYSIS_PROMPT = """Analyze this research article and extract the following information in JSON format:

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
   - "direct" if it contributes to understanding or addressing dyscalculia, including studies of dyscalculia, math education interventions, cognitive interventions for learning disabilities, research discussing dyscalculia in any context, or foundational cognitive science relevant to math learning, AND provides information that can be directly applied by educators and self-motivated adults addressing dyscalculia
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
{text}

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

TAG_EXPLANATION_PROMPT = """Analyze these tags from dyscalculia research and classify each one:

Tags: {tags}{research_context}

For each tag, determine:
1. tag_type: "direct" if directly related to dyscalculia/math learning disabilities, or "supportive" if providing context/methodology
2. dyscalculia_relevance: Brief explanation of relevance

Respond ONLY with JSON:
{{
  "tag1": {{"tag_type": "direct", "dyscalculia_relevance": "explanation"}},
  "tag2": {{"tag_type": "supportive", "dyscalculia_relevance": "explanation"}}
}}"""