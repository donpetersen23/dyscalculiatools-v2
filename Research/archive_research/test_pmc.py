from research_assistant import DyscalculiaResearchAssistant

# Create instance and test PMC search
assistant = DyscalculiaResearchAssistant()
results = assistant.search_pubmed_central("dyscalculia", 3)
print(f"\nFinal results: {results}")