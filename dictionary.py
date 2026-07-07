"""
dictionary.py — Local English dictionary helper for word verification.
Downloads a standard 10,000 common word list if missing, and offers
an embedded fallback list of common words for offline use.
"""

import os
import urllib.request
import threading
import string

DICTIONARY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")
WORD_LIST_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

# ── Fallback words (top ~300 common English words) ───────────────────────────
FALLBACK_WORDS = {
    "the", "of", "to", "and", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", 
    "as", "with", "his", "they", "i", "at", "be", "this", "have", "from", "or", "one", "had", "by", 
    "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", 
    "an", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about", "out", 
    "many", "then", "them", "these", "so", "some", "her", "would", "make", "like", "him", "into", 
    "time", "has", "look", "two", "more", "write", "go", "see", "number", "no", "way", "could", 
    "people", "my", "than", "first", "water", "been", "call", "who", "oil", "its", "now", "find", 
    "long", "down", "day", "did", "get", "come", "made", "may", "part", "over", "new", "sound", 
    "take", "only", "little", "work", "know", "place", "year", "live", "me", "back", "give", "most", 
    "very", "after", "thing", "our", "just", "name", "good", "sentence", "man", "think", "say", 
    "great", "where", "help", "through", "much", "before", "line", "right", "too", "mean", "old", 
    "any", "same", "tell", "boy", "follow", "came", "want", "show", "also", "around", "form", 
    "three", "small", "set", "end", "does", "another", "well", "large", "must", "big", "even", 
    "such", "because", "turn", "here", "why", "ask", "went", "men", "read", "need", "land", 
    "different", "home", "us", "move", "try", "kind", "hand", "picture", "again", "change", "off", 
    "play", "spell", "air", "away", "animal", "house", "point", "page", "letter", "mother", 
    "answer", "found", "study", "still", "learn", "should", "america", "world", "high", "every", 
    "near", "add", "food", "between", "own", "below", "country", "plant", "last", "school", 
    "father", "keep", "tree", "never", "start", "city", "earth", "eyes", "light", "thought", 
    "head", "under", "story", "saw", "left", "don't", "few", "while", "along", "might", "close", 
    "something", "seem", "next", "hard", "open", "example", "begin", "life", "always", "those", 
    "both", "paper", "together", "got", "group", "often", "run", "important", "until", "children", 
    "side", "feet", "car", "mile", "night", "walk", "white", "sea", "began", "grow", "took", 
    "river", "four", "carry", "state", "once", "book", "hear", "stop", "without", "second", 
    "late", "miss", "idea", "enough", "eat", "face", "watch", "far", "really", "almost", "let", 
    "above", "girl", "sometimes", "mountain", "cut", "young", "talk", "soon", "list", "song", 
    "leave", "family", "body", "music", "color", "stand", "sun", "questions", "fish", "area", 
    "mark", "dog", "horse", "birds", "problem", "complete", "room", "knew", "since", "ever", 
    "piece", "told", "usually", "didn't", "friends", "easy", "heard", "order", "red", "door", 
    "sure", "become", "top", "ship", "across", "today", "during", "short", "better", "best", 
    "however", "low", "hours", "black", "products", "happened", "whole", "measure", "remember", 
    "early", "waves", "reached", "wind", "rock", "space", "covered", "fast", "several", "hold", 
    "himself", "toward", "five", "step", "morning", "passed", "vowel", "true", "hundred", 
    "against", "pattern", "num", "table", "north", "slow", "map", "farm", "rule", "voice", 
    "seen", "cold", "cried", "plan", "notice", "south", "sing", "war", "ground", "fall", 
    "king", "town", "unit", "figure", "certain", "field", "travel", "wood", "fire", "upon"
}

class EnglishDictionary:
    def __init__(self):
        self.words = set(FALLBACK_WORDS)
        self.loaded = False
        self._lock = threading.Lock()
        
        # Load local file immediately if it exists
        self.load_local()

    def load_local(self):
        if os.path.exists(DICTIONARY_FILE):
            try:
                with open(DICTIONARY_FILE, "r", encoding="utf-8") as f:
                    local_words = set(line.strip().lower() for line in f if line.strip())
                if local_words:
                    with self._lock:
                        self.words = local_words
                        self.loaded = True
            except Exception as e:
                print(f"Error loading local dictionary: {e}")

    def download_in_background(self, callback_on_done=None):
        def _download():
            if not os.path.exists(DICTIONARY_FILE):
                try:
                    # Fetch from GitHub
                    req = urllib.request.Request(
                        WORD_LIST_URL, 
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        content = response.read().decode('utf-8')
                    
                    # Write to local file
                    with open(DICTIONARY_FILE, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    self.load_local()
                except Exception as e:
                    print(f"Background dictionary download failed: {e}")
            else:
                self.load_local()
            
            if callback_on_done:
                callback_on_done()

        thread = threading.Thread(target=_download, daemon=True)
        thread.start()

    def is_valid_word(self, raw_word: str) -> bool:
        # Strip all leading/trailing punctuation and convert to lowercase
        word = raw_word.strip(string.punctuation).lower()
        if not word:
            return False
        
        # Check if the word consists of only alphabetic characters or standard hyphens/apostrophes
        if not all(c.isalpha() or c in ("'", "-") for c in word):
            return False
            
        with self._lock:
            return word in self.words

# Global singleton
dictionary = EnglishDictionary()
