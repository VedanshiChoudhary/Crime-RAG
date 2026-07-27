import ollama


def generate_report(graph_data):

    prompt = f"""
You are a forensic investigation assistant.

Analyze the following crime records:

{graph_data}


Create a professional forensic investigation report.

Include:

1. Case ID
2. Crime type
3. Location
4. Date
5. Suspect description
6. Evidence analysis
7. Investigation summary
8. Recommendations


Rules:
- Use ONLY the provided crime records.
- Do NOT guess ethnicity, nationality, age, gender, or personal details.
- Do NOT add police actions, DNA, CCTV, fingerprints, or other evidence unless provided.
- Do NOT create information that is not present in the records.
- If information is missing, write "Not available".
- Keep the report factual and evidence-based.
- Clearly separate evidence from analysis.
- Do not claim that a suspect is identified unless the records confirm it.

"""


    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response["message"]["content"]



if __name__ == "__main__":

    sample_data = """

    Case ID: C001

    Crime Type: Robbery

    Location: Delhi

    Date: 2024-01-10

    Suspect:
    Unknown Male

    Evidence:
    black hair, oval face, scar on left cheek

    """


    report = generate_report(sample_data)


    print("\n========== FINAL FORENSIC REPORT ==========\n")

    print(report)
