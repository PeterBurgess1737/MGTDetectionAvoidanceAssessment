from paraphraser_helpers import paraphraser_server


def simple_paraphrase(string):
    return "paraphrase(" + string + ")"


paraphraser_server(simple_paraphrase)
