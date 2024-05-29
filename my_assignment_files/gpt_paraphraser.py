import pathlib

from openai import OpenAI

from paraphraser_helpers import paraphraser_server

MODEL = "gpt-3.5-turbo"

with open(pathlib.Path("my_assignment_files/api_key.txt"), "r") as f:
    api_key = f.read().strip()

CLIENT = OpenAI(api_key=api_key)

ROLE = ("When it comes to writing content, two factors are crucial, 'perplexity' and 'burstiness'. "
        "Perplexity measures the complexity of text. "
        "Separately, burstiness compares the variations of sentences. "
        "Humans tend to write with greater burstiness, for example, with some longer or complex sentences alongside "
        "shorter ones. "
        "AI sentences tend to be more uniform. "
        "Therefore, when writing the following content I am going to ask you to create, I need it to have a good "
        "amount of perplexity and burstiness. "
        "Rewrite this article with a high degree of perplexity and burstiness.")


def paraphrase_with_gpt(text):
    response = CLIENT.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ROLE},
            {"role": "user", "content": text}
        ]
    )

    return response.choices[0].message.content


paraphraser_server(paraphrase_with_gpt)
