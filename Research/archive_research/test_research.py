from research_assistant import DyscalculiaResearchAssistant

# Test the research assistant
assistant = DyscalculiaResearchAssistant()
print("Testing research assistant...")

# Test with a simple query
results = assistant.get_real_studies("number sense")
print(f"Found {len(results)} studies")

for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['title']}")
    print(f"   Database: {result['database']}")
    print(f"   Year: {result['year']}")