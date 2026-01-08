import pandas as pd
from groq_client import client

def ask_question(question):
    df = pd.read_excel("data/expenses.xlsx")
    context = df.to_string(index=False)

    prompt = f"""
Answer ONLY using this data:

{context}

Question:
{question}
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content
