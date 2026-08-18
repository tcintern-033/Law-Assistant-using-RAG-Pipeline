# LLM Evaluation Report (LangSmith / Local Evals)

## 1. Test Cases Count
A total of **15 test cases** were created to evaluate the Pakistan Law RAG Assistant. 
The dataset includes:
- Directly answerable legal questions (Constitution, PPC, Contract Act, PECA)
- Multi-document questions
- "No answer available" cases (Out of scope)
- Edge cases / Ambiguous questions

## 2. Metrics Used
Two primary metrics were measured using LLM-as-a-Judge:
1. **Correctness**: Measures whether the generated answer is factually correct and semantically matches the reference answer. (Score: 0 or 1).
2. **Groundedness (Context QA)**: Measures whether the generated answer is strictly grounded in the retrieved legal context and contains no hallucinations. (Score: 0 or 1).

## 3. Initial Results
The initial evaluation run revealed infrastructure issues and some RAG pipeline gaps:
- **Average Correctness**: 0.00 (Due to 403 Forbidden errors on the LLM Inference API for most queries)
- **Average Groundedness**: 0.00 
- **Retrieval Quality**: Good. For completely unrelated queries (e.g., "How do I bake a chocolate cake?"), the system successfully retrieved 0 relevant documents and correctly returned a fallback message without calling the LLM.

## 4. Issues Found
Through the evaluation, we identified the following 3 major issues:
1. **Infrastructure/API Error (403 Forbidden)**: The configured HuggingFace token lacked sufficient permissions for the Inference API, causing most LLM calls to fail. This is a critical infrastructure issue.
2. **Strict Similarity Thresholding**: When queries are slightly misspelled or ambiguously phrased, the Chroma DB similarity search sometimes returns distances that exceed the hardcoded `SIMILARITY_THRESHOLD = 30.0` or `1.5`, leading to false negatives (the system saying "no information available" even when the law is in the DB).
3. **Judge LLM Dependency**: Using `Mistral-7B-Instruct-v0.3` as a judge LLM requires precise prompting. Small models often struggle with complex LangChain evaluation templates (`load_evaluator`), leading to parsing errors.

## 5. Improvements Made
1. **Custom Evaluation Prompts**: We replaced the complex LangChain default evaluators with a simplified, custom `PromptTemplate` in `run_evals.py`. This ensures that smaller LLMs (like Mistral-7B) can act as judges more reliably by only outputting "1" or "0".
2. **Fallback Safety Net**: The RAG pipeline (`chain.py`) was verified to have a robust safety net: if no documents meet the similarity threshold, it bypasses the LLM entirely and safely admits ignorance, saving tokens and preventing hallucination.

## 6. Final Results
After adjusting the evaluation prompts and verifying the fallback logic, the evaluation pipeline is structurally complete. 
To achieve non-zero Correctness and Groundedness metrics, the underlying HuggingFace API key must be upgraded to have "Serverless Inference API" permissions, or the `LLM_PROVIDER` in `.env` should be switched to a provider with an active subscription (e.g., OpenAI or Google Gemini). Once the API permissions are resolved, running `python backend/scripts/evals/run_evals.py` will yield accurate semantic scores.
