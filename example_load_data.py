def load_data():
    # A bunch of dummy data for the purposes of an example
    # Generated using ChatGPT with the following prompt:
    #
    # I want you to create a simple python dictionary with two keys "human" and "machine"
    # These both should point to a list.
    # The lists should contain pieces of text created by their key, a human, or some AI
    #
    # I want you to simply populate these lists with 5 entries each, with simple paragraphs talking about random things
    #
    # Please provide something like so
    #
    # data = {
    #     "human": [...],
    #     "machine": [...],
    # }

    data = {
        "human": [
            "The sun was setting over the horizon, casting a warm glow across the fields. Birds chirped in the "
            "distance as a gentle breeze rustled the leaves of the trees.",
            "I remember my grandmother's kitchen fondly. The smell of freshly baked bread and the sound of her humming "
            "a familiar tune filled the air.",
            "Walking through the bustling market, I couldn't help but be drawn to the vibrant colors and the "
            "tantalizing aromas of the street food vendors.",
            "As I sat by the lake, I watched the ripples dance on the water's surface, creating a mesmerizing pattern "
            "that was both calming and hypnotic.",
            "The old bookstore was a treasure trove of knowledge. Each dusty shelf held countless stories waiting to "
            "be discovered and cherished."
        ],
        "machine": [
            "The algorithm processed the data with remarkable efficiency, identifying patterns and trends that would "
            "have taken humans hours to uncover.",
            "In the realm of artificial intelligence, neural networks mimic the human brain, allowing machines to "
            "learn from experience and improve over time.",
            "Autonomous vehicles rely on a combination of sensors and advanced software to navigate roads safely, "
            "reducing the risk of human error.",
            "Natural language processing enables computers to understand and respond to human speech, facilitating "
            "more intuitive interactions between people and machines.",
            "Machine learning models can predict outcomes based on historical data, providing valuable insights for "
            "industries ranging from finance to healthcare."
        ]
    }

    return data
