from research_assistant import DyscalculiaResearchAssistant

assistant = DyscalculiaResearchAssistant()
results = assistant.search_pubmed_central("dyscalculia", 10)

print(f"\nFound {len(results)} PMC articles:")
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['title']}")
    print(f"   Year: {result['year']}")
    print(f"   Abstract: {result['abstract'][:200]}...")
    print(f"   URL: {result['url']}")