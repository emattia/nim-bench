import wikipedia
import os

search_terms = [
    "Barack Obama",
    "Apple",
    "Swahili",
    "Amazon",
    "Jamba Juice",
    "Daniel Radcliffe",
    "The Office",
    "Fermat's Last Theorem",
    "The Grand Canyon",
    "Pittsburgh"
    "The Mona Lisa",
    "The Eiffel Tower",
    "Jane Austen",
    "John von Neumann",
    "The Great Depression",
    "Fall of the Berlin Wall",
    "Quantum entanglement",
    "Lincoln Logs",
    "Ferris Bueller",
    "Photosynthesis",
    "Murphy's law",
    "Mechanical Turk",
    "Georgia O'Keeffe",
    "Prince"
    "Sombrero"
]

def download_sample(term):
    key = term.replace(" ", "_").lower()
    if os.path.exists(f"data/{key}.txt"):
        print(f"Already have {term}")
        return
    try:
        page = wikipedia.page(term)
    except wikipedia.exceptions.PageError:
        print(f"Page not found for {term}")
        return
    except wikipedia.exceptions.DisambiguationError:
        print(f"Disambiguation error for {term}")
        return
    with open(f"data/{key}.txt", "w") as f:
        f.write(page.content)
    return

if __name__ == '__main__':
    for term in search_terms:
        download_sample(term)