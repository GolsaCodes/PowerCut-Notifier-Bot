import spell_checker1
from pathlib import Path
from score import score_keyboard_distance, score_context_similarity, score_bigram_occurrence, score_unigram_occurrence, \
    score_edit_distance
from utils import get_sentences_splitters, space_special_chars, text_normalization, delete_extra_space,de_space_special_chars
from semantic_errors1 import semantic_error_suggestions
# from semantic_error_v2 import load_homophones, semantic_error_suggestions_v2
import ahocorasick
from pathlib import Path
# Constants
ROOT_PATH = Path(__file__).parent
#data_path = Path(__file__).parent / "D:\\PycharmProjects\\Nevise_v3\\data"
default_words_path = ROOT_PATH / "dictionary_final.txt" 
# default_words_path = r"D:\PycharmProjects\Nevise_v3\Adata\dictionary_final_2.txt"
default_bigram_path = ROOT_PATH / "bigram_dictionary.txt"
# default_bigram_path = data_path / "bigrams.txt"
lemmas_path = ROOT_PATH / "lemmas.txt"
# lemmas_path = r"D:\PycharmProjects\Nevise_v3\Adata\lemmas.txt"


lemmas = []
with open(lemmas_path, "r", encoding="utf-8") as file:
    for line in file:
        lemma, count = line.strip().split("\t")
        lemmas.append(lemma)

words_derivations_path = ROOT_PATH / "words_derivations.txt"
words_derivations = []
with open(words_derivations_path, "r", encoding="utf-8") as file:
    for word in file:
        words_derivations.append(word.strip())


refined_dict = {}
word_refined_path = ROOT_PATH / "refined_pairs.txt"
with open(word_refined_path, "r", encoding="utf-8") as file:
    for line in file:
        word1, word2 = line.strip().split("----")
        refined_dict[word1] = word2


# Create an Aho-Corasick automaton
automaton = ahocorasick.Automaton()

# List of words to search for (including spaces)
keywords = refined_dict.keys()

# Add words to the automaton
for idx, keyword in enumerate(keywords):
    automaton.add_word(keyword, (idx, keyword))

# Build the Aho-Corasick trie
automaton.make_automaton()


homophones_dictionary_file = r"D:\PycharmProjects\Nevise_v3\data\dictionary_final_finglish.dat"

# Process the dictionary
# homophones = load_homophones(homophones_dictionary_file)


weights = {
    "edit_distance": 0.05,
    "keyboard_distance": 0.25,
    "context_similarity": 0.25,
    "bigram_occurrence": 0.30,
    "unigram_occurrence": 0.15
}

# Initialize SymSpell
sym_spell = spell_checker1.initialize_symspell(default_words_path, default_bigram_path)
frequencies = sym_spell.words.values()
min_frequency = min(frequencies)
max_frequency = max(frequencies)

bigram_frequencies = sym_spell.bigrams.values()
bigram_min_frequency = min(bigram_frequencies)
bigram_max_frequency = max(bigram_frequencies)


def preprocess_text(input_text):
    """Preprocess input text by spacing special characters and splitting into sentences."""
    input_text = text_normalization(input_text)
    spaced_text = space_special_chars(input_text)
    sentences, splitters = get_sentences_splitters(spaced_text)

    # new_sentences = []
    # for sentence in sentences:
    #     new_sentence = text_refinement(sentence, automaton, refined_dict)
    #     new_sentences.append(new_sentence)
    #     # if sentence != new_sentence:
    #     #     print(sentence)
    #     #     print(new_sentence)
    # sentences = new_sentences

    return sentences, splitters


def correct_sentence_errors(sentence, sym_spell, threshold1, threshold2, verbose=False):
    """
    Process a single sentence: identify and correct spelling errors using thresholds.
    Adds a verbose option to print debug information during processing.
    """

    sentence, misspelled_words, correct_words = spell_checker1.get_misspelled_words_with_suggestions(sentence, sym_spell,
                                                                                                    lemmas, words_derivations)

    semantic_suggestions = semantic_error_suggestions(sentence, sym_spell.words)
    # semantic_suggestions = semantic_error_suggestions_v2(sentence, homophones)
    changed_indices = {}

    if verbose:
        print(f"Processing sentence: {sentence}")
        print(f"Misspelled words: {misspelled_words}")
        print(f"Correct words: {correct_words}")
        print(f"Semantic suggestions: {semantic_suggestions}")

    for word, suggestions in misspelled_words.items():
        sentence, indices = apply_best_correction(sentence, word, suggestions, sym_spell, is_semantic=False,
                                                  verbose=verbose)
        for index, sugge in indices.items():
            changed_indices[index] = sugge


    for suggestion in semantic_suggestions:
        for word, suggestions in suggestion.items():
            sentence, indices = apply_best_correction(sentence, word, suggestions, sym_spell, is_semantic=True,
                                                      verbose=verbose)
            for index, sugge in indices.items():
                changed_indices[index] = sugge


    for word, suggestions in correct_words.items():
        sentence, indices = refine_correct_words(sentence, word, suggestions, sym_spell, threshold1, threshold2,
                                                 verbose=verbose)
        for index, sugge in indices.items():
            changed_indices[index] = sugge


    if verbose:
        print(f"Corrected sentence: {sentence}")

    return sentence, changed_indices


def refine_correct_words(sentence, word, suggestions, sym_spell, threshold1, threshold2, verbose=False):
    if verbose:
        print(f"Correct Word: {word}")
        print(f"Suggestions: {', '.join(suggestions) if suggestions else 'No suggestions'}")

    new_weights = {
        "edit_distance": 0.1,
        "keyboard_distance": 0.1,
        "context_similarity": 0.25,
        "bigram_occurrence": 0.30,
        "unigram_occurrence": 0
    }

    best_suggestion = word  # Default to the original word
    words = sentence.split()
    changed_indices = {}

    for i, w in enumerate(words):
       # print(w)
        if w == word:
            context_score = score_context_similarity(words, i, word)
            bigram_score = score_bigram_occurrence(words, i, word, sym_spell.bigrams, bigram_max_frequency)
            # weighted_score = (
            #     new_weights["context_similarity"] * context_score +
            #     new_weights["bigram_occurrence"] * bigram_score
            # )
            # best_score = weighted_score
            #
            if verbose:
                print(f"Initial scores for '{word}':")
                print(f"  Context Similarity Score: {context_score}")
                print(f"  Bigram Occurrence Score: {bigram_score}")
                # print(f"  Weighted Score: {weighted_score}")

            if context_score + bigram_score < threshold1:

                edit_distance_score = 1
                keyboard_score = 1
                unigram_score = score_unigram_occurrence(words[i], sym_spell.words, max_frequency)

                weighted_score = (
                        new_weights["edit_distance"] * edit_distance_score +
                        new_weights["keyboard_distance"] * keyboard_score +
                        new_weights["context_similarity"] * context_score +
                        new_weights["bigram_occurrence"] * bigram_score +
                        new_weights["unigram_occurrence"] * unigram_score
                )
                best_score = weighted_score

                if verbose:
                    print(f"Initial scores for '{word}':")
                    print(f"  Edit Distance Score: {edit_distance_score}")
                    print(f"  Keyboard Distance Score: {keyboard_score}")
                    print(f"  Context Similarity Score: {context_score}")
                    print(f"  Bigram Occurrence Score: {bigram_score}")
                    print(f"  Unigram Occurrence Score: {unigram_score}")
                    print(f"  Weighted Score: {weighted_score}")

                for suggestion in suggestions:
                    context_score = score_context_similarity(words, i, suggestion)
                    bigram_score = score_bigram_occurrence(words, i, suggestion, sym_spell.bigrams, bigram_max_frequency)
                    if context_score + bigram_score > threshold2:
                        edit_distance_score = score_edit_distance(word, suggestion)
                        keyboard_score = score_keyboard_distance(word, suggestion)
                        unigram_score = score_unigram_occurrence(suggestion, sym_spell.words, max_frequency)
                        weighted_score = (
                                new_weights["edit_distance"] * edit_distance_score +
                                new_weights["keyboard_distance"] * keyboard_score +
                                new_weights["context_similarity"] * context_score +
                                new_weights["bigram_occurrence"] * bigram_score +
                                new_weights["unigram_occurrence"] * unigram_score
                        )

                        if verbose:
                            print(f"Suggestion: {suggestion}")
                            print(f"  Edit Distance Score: {edit_distance_score}")
                            print(f"  Keyboard Distance Score: {keyboard_score}")
                            print(f"  Context Similarity Score: {context_score}")
                            print(f"  Bigram Occurrence Score: {bigram_score}")
                            print(f"  Unigram Occurrence Score: {unigram_score}")
                            print(f"  Weighted Score: {weighted_score}")

                        if weighted_score > best_score:
                            best_score = weighted_score
                            best_suggestion = suggestion

                if verbose:
                    print(f"Best suggestion for '{word}' is '{best_suggestion}' with score {best_score}")

                # words[i] = best_suggestion
                if best_suggestion != word:
                    words[i] = best_suggestion
                    changed_indices[i] = best_suggestion

            return " ".join(words), changed_indices

    return " ".join(words), changed_indices


def apply_best_correction(sentence, word, suggestions, sym_spell, is_semantic=False, verbose=False):
    """Find the best suggestion for a misspelled word and replace it by index in the sentence."""
    best_suggestion = word  # Default to the original word
    best_score = -1
    changed_indices = {}

    if not suggestions:
        return sentence, changed_indices  # No suggestions, return the sentence as is

    if verbose:
        print(f"Misspelled Word: {word}")
        print(f"Suggestions: {', '.join(suggestions) if suggestions else 'No suggestions'}")


    if is_semantic:
        weights = {
            "edit_distance": 0.03,
            "keyboard_distance": 0.07,
            "context_similarity": 0.4,
            "bigram_occurrence": 0.4,
            "unigram_occurrence": 0.1
        }

    else:
        weights ={
            "edit_distance": 0.05,
            "keyboard_distance": 0.25,
            "context_similarity": 0.25,
            "bigram_occurrence": 0.30,
            "unigram_occurrence": 0.15
        }


    words = sentence.split()  # Split the sentence into a list of words
    for i, current_word in enumerate(words):
        if current_word == word:  # Find the index of the word to replace
            for suggestion in suggestions:
                # Calculate scores
                # edit_distance_score = score_edit_distance(word, suggestion) if not is_semantic else 0
                # keyboard_score = score_keyboard_distance(word, suggestion) if not is_semantic else 0
                edit_distance_score = score_edit_distance(word, suggestion)
                keyboard_score = score_keyboard_distance(word, suggestion)
                context_score = score_context_similarity(words, i, suggestion)
                bigram_score = score_bigram_occurrence(words, i, suggestion, sym_spell.bigrams, bigram_max_frequency)
                unigram_score = score_unigram_occurrence(suggestion, sym_spell.words, max_frequency)

                # Calculate weighted score
                weighted_score = (
                        weights["edit_distance"] * edit_distance_score +
                        weights["keyboard_distance"] * keyboard_score +
                        weights["context_similarity"] * context_score +
                        weights["bigram_occurrence"] * bigram_score +
                        weights["unigram_occurrence"] * unigram_score
                )

                if verbose:
                    print(f"Suggestion: {suggestion}")
                    print(f"  Edit Distance Score: {edit_distance_score}")
                    print(f"  Keyboard Distance Score: {keyboard_score}")
                    print(f"  Context Similarity Score: {context_score}")
                    print(f"  Bigram Occurrence Score: {bigram_score}")
                    print(f"  Unigram Occurrence Score: {unigram_score}")
                    print(f"  Weighted Score: {weighted_score}")

                # Update the best suggestion
                if weighted_score > best_score:
                    best_score = weighted_score
                    best_suggestion = suggestion

            if verbose:
                print(f"Best suggestion for '{word}' is '{best_suggestion}' with score {best_score}")

            # Replace the word at the specific index with the best suggestion
            # words[i] = best_suggestion
            if best_suggestion != word:
                words[i] = best_suggestion
                changed_indices[i] = best_suggestion

    return " ".join(words), changed_indices  # Join the list back into a sentence


def text_refinement(text,automaton, refined_dict):
    """
    Replaces words in the text using an Aho-Corasick automaton and a refinement dictionary.

    Args:
        text (str): The input text.
        refined_dict (dict): Dictionary mapping words to their refined versions.

    Returns:
        str: The refined text with replacements applied.
    """
    
    matches = []
    for end_index, (idx, keyword) in automaton.iter(text):
        start_index = end_index - len(keyword) + 1
        matches.append((keyword, start_index, end_index))

    for match in matches:
        keyword, start_index, end_index = match
        new_word = refined_dict[keyword]

        if end_index + 1 < len(text):
            if ((text[start_index - 1] == " " and text[end_index + 1] == " ") or
                    (start_index == 0 and text[end_index + 1] == " ")):
                text = text[:start_index] + new_word + text[end_index + 1:]

        if end_index + 1 == len(text):
            if (text[start_index - 1] == " " and (end_index + 1) == len(text)) or (start_index == 0 and (end_index + 1) == len(text)):
                text = text[:start_index] + new_word + text[end_index + 1:]

    return text

def correct_full_text(input_text, threshold1, threshold2, verbose=False):
    """Correct the entire input text with provided thresholds."""
    sentences, splitters = preprocess_text(input_text)
    corrected_sentences = [
        correct_sentence_errors(sentence, sym_spell, threshold1, threshold2, verbose)[0] for sentence in sentences
    ]

    new_sentences = []
    for sentence in corrected_sentences:
        new_sentence = text_refinement(sentence, automaton, refined_dict)
        new_sentences.append(new_sentence)
        # if sentence != new_sentence:
        #     print(sentence)
        #     print(new_sentence)

    corrected_sentences = new_sentences

    final_text = "".join([sentence + splitter for sentence, splitter in zip(corrected_sentences, splitters)])
    if len(sentences) > len(splitters):
        final_text += corrected_sentences[-1]

    # final_text = de_space_special_chars(final_text)
    # final_text = delete_extra_space(final_text)
    return final_text


def main():
    print("Type a sentence to check spelling (type 'terminate' to stop):")
    while True:
        input_text = input("Enter a sentence: ").strip()
        if input_text.lower() == "terminate":
            print("Spell-checking session ended.")
            break
        corrected_text = correct_full_text(input_text, 0.35, 0.70, verbose=True)
        print(f"\nCorrected Text:\n{corrected_text}")


if __name__ == "__main__":
    main()