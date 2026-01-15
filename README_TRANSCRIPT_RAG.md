# Transcript RAG System

This directory contains a RAG (Retrieval-Augmented Generation) system built on podcast transcripts using the RAG-Anything package.

## Transcripts

The system includes two podcast transcripts from Lenny's Podcast:

1. **Ada Chen Rekhi.txt** - Executive coach and co-founder of Notejoy
   - Topics: Curiosity loops, career strategy, values exercises, working with partners

2. **Adam Fishman.txt** - Former VP of Growth at Lyft and Patreon
   - Topics: Growth competency model, onboarding optimization, company selection framework

## Setup Instructions

### Prerequisites

1. **Install the package** (already done):
   ```bash
   pip install raganything
   ```

2. **Set up OpenAI API key**:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

   Get your API key from: https://platform.openai.com/api-keys

### Build the RAG System

Run the provided script to index the transcripts:

```bash
python build_transcript_rag.py
```

This script will:
- Initialize the RAG system with LightRAG
- Process both transcript files
- Build a knowledge graph from the content
- Create embeddings for semantic search

## Sample Questions

Here are example questions you can ask the RAG system:

### About Ada Chen Rekhi:

1. **What is a curiosity loop and how does it work?**
   - Learn about Ada's structured approach to gathering advice

2. **What are Ada's personal values?**
   - Understand the values exercise and how to apply it

3. **What advice does Ada give about building an early career?**
   - Explore the "explore and exploit" framework

4. **What is the 'eating your vegetables' concept?**
   - Learn about developing skills through deliberate practice

5. **Should you start a company with your partner?**
   - Hear Ada's experience and advice on co-founding with a spouse

6. **What is the explore and exploit framework for career development?**
   - Understand when to explore new opportunities vs. double down

7. **How do you avoid being the 'boiled frog' in your career?**
   - Learn to recognize when it's time to make a change

### About Adam Fishman:

8. **What is Adam Fishman's growth competency model?**
   - Understand the framework for hiring and evaluating growth people

9. **What are the four main components of the growth competency model?**
   - Growth execution, customer knowledge, growth strategy, communication & influence

10. **Why is onboarding important for growth?**
    - Learn about the outsized impact of onboarding optimization

11. **What is the PMF framework for choosing a company to work at?**
    - People, Mission, Financials - how to evaluate job opportunities

12. **How can onboarding improve retention?**
    - Real examples of 10-25% improvements in cohort retention

13. **What mistakes do founders make when hiring growth people?**
    - Common pitfalls and how to avoid them

## Query the RAG System

Once the RAG is built, you can query it with:

```python
import asyncio
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm import openai_complete_if_cache, openai_embedding
from lightrag.utils import EmbeddingFunc
import numpy as np

async def query_rag(question: str):
    # Configure RAG
    config = RAGAnythingConfig(working_dir="./rag_storage")

    # Set up LLM functions
    async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return await openai_complete_if_cache(
            "gpt-4o-mini", prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            **kwargs
        )

    async def embedding_func(texts: list[str]) -> np.ndarray:
        return await openai_embedding(texts, model="text-embedding-3-small")

    # Initialize RAG
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=8192,
            func=embedding_func
        )
    )

    # Ensure LightRAG is initialized
    await rag._ensure_lightrag_initialized()

    # Query the RAG
    response = await rag.aquery(question, mode="hybrid")
    print(f"\nQuestion: {question}")
    print(f"\nAnswer:\n{response}\n")

    rag.close()

# Example usage
asyncio.run(query_rag("What is a curiosity loop and how does it work?"))
```

## Query Modes

The RAG system supports different query modes:

- **`naive`**: Simple keyword search
- **`local`**: Local context-based search
- **`global`**: Global knowledge graph search
- **`hybrid`**: Combines local and global (recommended)
- **`mix`**: Mixes multiple approaches

## Tips for Best Results

1. **Be specific**: Ask focused questions rather than broad topics
2. **Use names**: Mention "Ada" or "Adam" to get person-specific insights
3. **Ask about frameworks**: The transcripts contain many frameworks and models
4. **Follow up**: Ask clarifying questions based on initial responses

## File Structure

```
rag-anything/
├── data/
│   ├── Ada Chen Rekhi.txt
│   └── Adam Fishman.txt
├── rag_storage/          # Generated after building RAG
├── build_transcript_rag.py
├── query_rag.py          # Simple query script
└── README_TRANSCRIPT_RAG.md
```

## Troubleshooting

### "OPENAI_API_KEY not set"
- Make sure you export the API key in your terminal session
- Or add it to your `.env` file

### "ModuleNotFoundError: No module named 'raganything'"
- Activate the correct conda environment
- Or reinstall: `pip install raganything`

### Memory issues
- The transcripts are large (~80-90KB each)
- Ensure you have enough RAM
- Consider processing one transcript at a time if needed

## Cost Estimate

Building the RAG system will use OpenAI API:
- Embeddings: ~$0.01-0.02 per transcript
- Knowledge graph extraction: ~$0.10-0.20 total
- Queries: ~$0.001-0.01 per query

Total setup cost: **~$0.25**

## Next Steps

1. Build the RAG system with the provided script
2. Try the sample questions
3. Explore the transcripts with your own questions
4. Combine insights from both Ada and Adam on career and growth topics!
