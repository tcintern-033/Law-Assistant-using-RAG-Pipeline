import os
from langsmith import Client

# Initialize LangSmith client
# Requires LANGCHAIN_API_KEY environment variable to be set
client = Client()

dataset_name = "RAG Law Assistant Evals"
dataset_description = "Evaluation dataset for the Pakistan Law RAG Assistant."

# Create the dataset if it doesn't exist
try:
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=dataset_description,
    )
    print(f"Created dataset: {dataset.name}")
except Exception as e:
    print(f"Dataset might already exist or error occurred: {e}")
    # Try fetching it
    dataset = client.read_dataset(dataset_name=dataset_name)
    print(f"Using existing dataset: {dataset.name}")

# 15 Test cases (Direct, Multi-document, Out-of-scope, Edge cases)
examples = [
    # Directly answerable questions
    ("What are the fundamental rights of citizens according to the Constitution of Pakistan?", "The fundamental rights include equality before law, right to fair trial, freedom of speech, freedom of religion, etc."),
    ("What is the punishment for cyber terrorism under PECA 2016?", "Under PECA 2016, cyber terrorism is punishable with imprisonment which may extend to 14 years or with fine which may extend to 50 million rupees or both."),
    ("According to the Contract Act 1872, what constitutes a valid contract?", "A valid contract requires offer, acceptance, lawful consideration, lawful object, competent parties, and free consent."),
    ("What is 'Qatl-i-Amd' under the Pakistan Penal Code?", "Qatl-i-Amd is defined as whoever, with the intention of causing death or with the intention of causing bodily injury to a person, causes the death of such person, commits qatl-i-amd (intentional murder)."),
    ("Who can be appointed as a Judge of the Supreme Court of Pakistan?", "A person who is a citizen of Pakistan and has been a judge of a High Court for at least five years or an advocate of a High Court for at least fifteen years."),
    
    # Multi-document / Comparative
    ("Does a contract made through electronic means have legal validity?", "Yes, PECA 2016 and related laws provide legal recognition to electronic communications and contracts made through electronic means."),
    ("How does PECA 2016 intersect with the Penal Code regarding defamation?", "PECA covers defamation in cyberspace (e.g., section 20 on offenses against dignity of a natural person), while the PPC covers traditional criminal defamation."),
    ("Is a contract involving an illegal act under the PPC valid?", "No, under the Contract Act, an agreement with an unlawful object (such as an act prohibited by the PPC) is void."),
    
    # "No answer available" cases (Out of scope)
    ("What are the traffic rules in New York City?", "The available legal documents do not contain enough information to answer this question reliably."),
    ("How do I bake a chocolate cake?", "The available legal documents do not contain enough information to answer this question reliably."),
    ("What is the legal status of space travel in Pakistan?", "The available legal documents do not contain enough information to answer this question reliably."),
    
    # Edge cases (Ambiguous, Complex)
    ("What is the punishment for theft?", "The punishment for theft (Sarqa) depends on the specific circumstances and value of stolen property under the Pakistan Penal Code. It can range from imprisonment to amputation in Hadd cases."),
    ("Can a minor enter into a contract?", "Under the Contract Act 1872, an agreement by a minor is generally void ab initio (invalid from the start), as a minor is not competent to contract."),
    ("What happens if a person is forced to sign a contract at gunpoint?", "Under the Contract Act, a contract signed at gunpoint lacks free consent (it involves coercion), making the contract voidable at the option of the aggrieved party. The act of pointing a gun also constitutes an offense under the PPC."),
    ("Is hate speech on Facebook a crime?", "Yes, under PECA 2016, hate speech and offenses against the dignity of a natural person on electronic platforms (like Facebook) are punishable crimes.")
]

# Create examples in LangSmith
count = 0
for q, a in examples:
    try:
        client.create_example(
            inputs={"question": q},
            outputs={"answer": a},
            dataset_id=dataset.id,
        )
        count += 1
    except Exception as e:
        print(f"Failed to create example '{q}': {e}")

print(f"Successfully added {count} examples to the dataset.")
