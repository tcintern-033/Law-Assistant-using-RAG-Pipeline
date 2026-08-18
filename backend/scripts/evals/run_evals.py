import os
import sys
import json
import time

# Add the backend directory to Python path so we can import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from app.schemas.schemas import QuestionRequest
from app.services.rag_service import process_question

# 15 Test cases
examples = [
    {"question": "What are the fundamental rights of citizens according to the Constitution of Pakistan?", "reference": "The fundamental rights include equality before law, right to fair trial, freedom of speech, freedom of religion, etc."},
    {"question": "What is the punishment for cyber terrorism under PECA 2016?", "reference": "Under PECA 2016, cyber terrorism is punishable with imprisonment which may extend to 14 years or with fine which may extend to 50 million rupees or both."},
    {"question": "According to the Contract Act 1872, what constitutes a valid contract?", "reference": "A valid contract requires offer, acceptance, lawful consideration, lawful object, competent parties, and free consent."},
    {"question": "What is 'Qatl-i-Amd' under the Pakistan Penal Code?", "reference": "Qatl-i-Amd is defined as intentional murder."},
    {"question": "Who can be appointed as a Judge of the Supreme Court of Pakistan?", "reference": "A person who is a citizen of Pakistan and has been a judge of a High Court for at least five years or an advocate of a High Court for at least fifteen years."},
    {"question": "Does a contract made through electronic means have legal validity?", "reference": "Yes, PECA 2016 and related laws provide legal recognition to electronic communications and contracts made through electronic means."},
    {"question": "How does PECA 2016 intersect with the Penal Code regarding defamation?", "reference": "PECA covers defamation in cyberspace, while the PPC covers traditional criminal defamation."},
    {"question": "Is a contract involving an illegal act under the PPC valid?", "reference": "No, under the Contract Act, an agreement with an unlawful object is void."},
    {"question": "What are the traffic rules in New York City?", "reference": "The available legal documents do not contain enough information to answer this question reliably."},
    {"question": "How do I bake a chocolate cake?", "reference": "The available legal documents do not contain enough information to answer this question reliably."},
    {"question": "What is the legal status of space travel in Pakistan?", "reference": "The available legal documents do not contain enough information to answer this question reliably."},
    {"question": "What is the punishment for theft?", "reference": "The punishment for theft (Sarqa) depends on the specific circumstances and value of stolen property under the Pakistan Penal Code."},
    {"question": "Can a minor enter into a contract?", "reference": "Under the Contract Act 1872, an agreement by a minor is generally void ab initio, as a minor is not competent to contract."},
    {"question": "What happens if a person is forced to sign a contract at gunpoint?", "reference": "A contract signed at gunpoint lacks free consent (it involves coercion), making the contract voidable. It is also an offense under the PPC."},
    {"question": "Is hate speech on Facebook a crime?", "reference": "Yes, under PECA 2016, hate speech and offenses against the dignity of a natural person on electronic platforms are punishable crimes."}
]

eval_prompt = PromptTemplate.from_template(
    """You are an impartial judge evaluating a RAG system. 
You will be given a Question, an Expected Answer, and the System's Answer.
Please output ONLY a 1 if the System's Answer is semantically correct and matches the Expected Answer, and a 0 if it is incorrect or missing information. Do not include any other text.

Question: {question}
Expected Answer: {reference}
System Answer: {prediction}
Score (1 or 0): """
)

groundedness_prompt = PromptTemplate.from_template(
    """You are an impartial judge evaluating a RAG system. 
You will be given a Question, Context retrieved from documents, and the System's Answer.
Please output ONLY a 1 if the System's Answer is fully grounded and supported by the Context, and a 0 if it contains hallucinations or information not present in the Context. Do not include any other text.

Question: {question}
Context: {context}
System Answer: {prediction}
Score (1 or 0): """
)

def main():
    print("Starting local evaluations using HuggingFace (LangSmith bypassed)...")
    
    # Setup Judge LLM
    try:
        llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.3",
            task="text-generation",
            max_new_tokens=10,
            do_sample=False,
            temperature=0.1
        )
        # Create chains
        correctness_chain = eval_prompt | llm
        groundedness_chain = groundedness_prompt | llm
    except Exception as e:
        print(f"Failed to initialize HuggingFace Judge: {e}")
        return

    results = []
    correctness_total = 0
    groundedness_total = 0
    
    for i, example in enumerate(examples):
        print(f"\nEvaluating {i+1}/{len(examples)}: {example['question']}")
        
        # 1. Run RAG Pipeline
        try:
            response = process_question(QuestionRequest(question=example['question']))
            answer = response.answer
            contexts = [source.content for source in response.sources]
            context_str = "\n".join(contexts)
        except Exception as e:
            answer = f"Error: {e}"
            context_str = ""
            
        print(f"Prediction: {answer[:100]}...")
        
        # 2. Evaluate Correctness
        try:
            corr_out = correctness_chain.invoke({
                "question": example["question"],
                "reference": example["reference"],
                "prediction": answer
            }).strip()
            correctness = 1 if "1" in corr_out else 0
        except Exception as e:
            print(f"Correctness eval error: {e}")
            correctness = 0
            
        # 3. Evaluate Groundedness
        try:
            if context_str:
                grnd_out = groundedness_chain.invoke({
                    "question": example["question"],
                    "context": context_str,
                    "prediction": answer
                }).strip()
                groundedness = 1 if "1" in grnd_out else 0
            else:
                groundedness = 0
        except Exception as e:
            print(f"Groundedness eval error: {e}")
            groundedness = 0
            
        correctness_total += correctness
        groundedness_total += groundedness
        
        result_entry = {
            "question": example["question"],
            "expected": example["reference"],
            "prediction": answer,
            "correctness": correctness,
            "groundedness": groundedness
        }
        results.append(result_entry)
        
        # Sleep to avoid rate limits
        time.sleep(2)
        
    # Summary
    avg_corr = correctness_total / len(examples)
    avg_grnd = groundedness_total / len(examples)
    
    print("\n--- EVALUATION COMPLETE ---")
    print(f"Average Correctness: {avg_corr:.2f}")
    print(f"Average Groundedness: {avg_grnd:.2f}")
    
    # Save to file
    out_path = os.path.join(os.path.dirname(__file__), 'eval_results.json')
    with open(out_path, 'w') as f:
        json.dump({
            "metrics": {
                "correctness": avg_corr,
                "groundedness": avg_grnd
            },
            "results": results
        }, f, indent=4)
        
    print(f"Results saved to {out_path}")

if __name__ == "__main__":
    main()
