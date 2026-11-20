
import re
from collections import Counter

# Attempt NLTK imports for stemming and lemmatization
try:
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.corpus import wordnet
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False
    PorterStemmer = None
    WordNetLemmatizer = None
    wordnet = None

# Attempt NLTK VADER sentiment analyzer import
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except Exception:
    VADER_AVAILABLE = False
    SentimentIntensityAnalyzer = None

# Attempt scikit-learn imports for LDA topic modeling
try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False
    CountVectorizer = None
    LatentDirichletAllocation = None


class NLPProcessor:
    """Process interview answers and extract useful text features."""

    def __init__(self):
        self.stop_words = {
            "a", "an", "the", "is", "am", "are", "was", "were",
            "be", "been", "being", "to", "of", "in", "on", "at",
            "for", "and", "or", "but", "with", "by", "as", "it",
            "this", "that", "these", "those", "i", "we", "you",
            "he", "she", "they", "my", "our", "your", "their",
            "do", "does", "did", "have", "has", "had", "can",
            "could", "would", "should", "will", "from", "into"
        }

        self.technical_skills = {
            "python", "java", "c++", "sql", "machine learning",
            "deep learning", "artificial intelligence", "nlp",
            "natural language processing", "flask", "django",
            "tensorflow", "pytorch", "scikit-learn", "numpy",
            "pandas", "data science", "neural networks",
            "database", "html", "css", "javascript", "rest api",
            "api", "classification", "regression", "clustering",
            "random forest", "decision tree", "llm", "rag"
        }

        # Initialize stemmer and lemmatizer if NLTK is available
        self._stemmer = PorterStemmer() if NLTK_AVAILABLE else None
        self._lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None

        # Initialize VADER sentiment analyzer if available
        self._sentiment_analyzer = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None

        # LDA components (lazy initialization)
        self._lda_vectorizer = None
        self._lda_model = None
        self._lda_fitted = False

    def clean_text(self, text):
        """Normalize text while preserving common technical symbols."""

        if not isinstance(text, str):
            raise TypeError("Answer must be a string.")

        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-z0-9+#.\s/-]", "", text)

        return text

    def tokenize(self, text):
        """Split normalized text into tokens."""

        cleaned_text = self.clean_text(text)
        return re.findall(r"[a-z0-9]+(?:[+#.-][a-z0-9+#.-]*)*", cleaned_text)

    def extract_keywords(self, text):
        """Extract informative words, excluding common stop words."""

        tokens = self.tokenize(text)

        keywords = [
            token for token in tokens
            if token not in self.stop_words and len(token) > 1
        ]

        return keywords

    def extract_skills(self, text):
        """Find known technical skills mentioned in the answer."""

        cleaned_text = self.clean_text(text)
        found_skills = []

        # Match longer phrases before shorter ones.
        for skill in sorted(
            self.technical_skills,
            key=len,
            reverse=True
        ):
            pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"

            if re.search(pattern, cleaned_text):
                found_skills.append(skill)

        return sorted(found_skills)

    def _get_pos_tag(self, word):
        """Map NLTK POS tag to WordNet POS tag for lemmatization."""
        if not NLTK_AVAILABLE:
            return wordnet.NOUN

        # Simple heuristic: if word ends with common verb suffixes, treat as verb
        if word.endswith(('ing', 'ed', 'es', 's')) and len(word) > 3:
            return wordnet.VERB
        elif word.endswith(('ly',)):
            return wordnet.ADV
        elif word.endswith(('tion', 'sion', 'ment', 'ness', 'ity', 'er', 'or')):
            return wordnet.NOUN
        elif word.endswith(('able', 'ible', 'ful', 'less', 'ous', 'ive')):
            return wordnet.ADJ
        return wordnet.NOUN

    def stem(self, text):
        """Apply Porter stemming to tokens in text."""
        if not NLTK_AVAILABLE or self._stemmer is None:
            # Fallback: return original tokens if NLTK not available
            return self.tokenize(text)

        tokens = self.tokenize(text)
        return [self._stemmer.stem(token) for token in tokens]

    def lemmatize(self, text):
        """Apply WordNet lemmatization to tokens in text."""
        if not NLTK_AVAILABLE or self._lemmatizer is None:
            # Fallback: return original tokens if NLTK not available
            return self.tokenize(text)

        tokens = self.tokenize(text)
        return [self._lemmatizer.lemmatize(token, pos=self._get_pos_tag(token)) for token in tokens]

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of the text using VADER.
        Returns a dict with 'compound', 'positive', 'negative', 'neutral' scores.
        """
        if not VADER_AVAILABLE or self._sentiment_analyzer is None:
            # Fallback: return neutral scores
            return {
                "compound": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0,
                "label": "neutral"
            }

        scores = self._sentiment_analyzer.polarity_scores(text)
        compound = scores["compound"]

        # Determine label based on compound score
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "compound": round(compound, 4),
            "positive": round(scores["pos"], 4),
            "negative": round(scores["neg"], 4),
            "neutral": round(scores["neu"], 4),
            "label": label
        }

    def _get_lda_stopwords(self):
        """Extended stopwords for LDA including technical terms that aren't topic-revealing."""
        base_stopwords = set(self.stop_words)
        # Add common technical words that appear frequently but don't define topics
        technical_stopwords = {
            "use", "using", "used", "work", "working", "works", "like", "way",
            "think", "know", "understand", "explain", "example", "examples",
            "how", "what", "why", "when", "where", "which", "who",
            "also", "even", "still", "just", "really", "very", "much",
            "need", "needs", "needed", "want", "wants", "wanted",
            "can", "could", "would", "should", "will", "may", "might",
            "one", "two", "three", "first", "second", "third"
        }
        return base_stopwords.union(technical_stopwords)

    def extract_topics_lda(self, documents, n_topics=3, n_words=5):
        """
        Extract topics from a collection of documents using LDA.

        Args:
            documents: List of text strings (e.g., multiple interview answers)
            n_topics: Number of topics to extract
            n_words: Number of top words per topic

        Returns:
            Dict with 'topics' (list of topic word lists) and 'topic_distributions' (per-doc distributions)
        """
        if not SKLEARN_AVAILABLE or CountVectorizer is None or LatentDirichletAllocation is None:
            return {
                "topics": [],
                "topic_distributions": [],
                "note": "scikit-learn not available for LDA"
            }

        if not documents or len(documents) < 2:
            return {
                "topics": [],
                "topic_distributions": [],
                "note": "Need at least 2 documents for LDA"
            }

        try:
            # Clean documents
            cleaned_docs = [self.clean_text(doc) for doc in documents]
            cleaned_docs = [doc for doc in cleaned_docs if len(doc.strip()) > 10]

            if len(cleaned_docs) < 2:
                return {
                    "topics": [],
                    "topic_distributions": [],
                    "note": "Insufficient valid documents after cleaning"
                }

            # Vectorize with custom stopwords
            stopwords = self._get_lda_stopwords()
            self._lda_vectorizer = CountVectorizer(
                max_df=0.95,
                min_df=1,
                stop_words=list(stopwords),
                token_pattern=r'[a-z]{3,}',  # Only words 3+ chars
                max_features=100
            )

            doc_term_matrix = self._lda_vectorizer.fit_transform(cleaned_docs)

            # Fit LDA
            n_topics_actual = min(n_topics, len(cleaned_docs))
            self._lda_model = LatentDirichletAllocation(
                n_components=n_topics_actual,
                random_state=42,
                max_iter=10,
                learning_method='online'
            )
            self._lda_model.fit(doc_term_matrix)
            self._lda_fitted = True

            # Extract topic words
            feature_names = self._lda_vectorizer.get_feature_names_out()
            topics = []

            for topic_idx, topic in enumerate(self._lda_model.components_):
                top_words_idx = topic.argsort()[:-n_words-1:-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topics.append(top_words)

            # Get topic distributions for each document
            topic_distributions = self._lda_model.transform(doc_term_matrix)
            topic_distributions = topic_distributions.round(4).tolist()

            return {
                "topics": topics,
                "topic_distributions": topic_distributions,
                "n_topics": n_topics_actual,
                "documents_analyzed": len(cleaned_docs)
            }

        except Exception as e:
            return {
                "topics": [],
                "topic_distributions": [],
                "note": f"LDA failed: {str(e)}"
            }

    def get_answer_topics(self, answer, reference_documents=None):
        """
        Get topic distribution for a single answer.
        If reference_documents provided, fits LDA on them first.
        Otherwise uses pre-fitted model or returns empty.
        """
        if reference_documents:
            # Fit on reference documents + current answer
            all_docs = reference_documents + [answer]
            result = self.extract_topics_lda(all_docs)
            if result["topic_distributions"]:
                # Return distribution for the last document (current answer)
                return {
                    "topic_distribution": result["topic_distributions"][-1],
                    "topics": result["topics"],
                    "n_topics": result.get("n_topics", 0)
                }
            return {"topic_distribution": [], "topics": [], "n_topics": 0}

        elif self._lda_fitted and self._lda_vectorizer and self._lda_model:
            # Use pre-fitted model
            try:
                cleaned = self.clean_text(answer)
                doc_term = self._lda_vectorizer.transform([cleaned])
                dist = self._lda_model.transform(doc_term)[0].round(4).tolist()

                feature_names = self._lda_vectorizer.get_feature_names_out()
                topics = []
                for topic_idx, topic in enumerate(self._lda_model.components_):
                    top_words_idx = topic.argsort()[:-6:-1]
                    top_words = [feature_names[i] for i in top_words_idx]
                    topics.append(top_words)

                return {
                    "topic_distribution": dist,
                    "topics": topics,
                    "n_topics": len(topics)
                }
            except Exception:
                pass

        return {"topic_distribution": [], "topics": [], "n_topics": 0}

    def analyze_answer(self, text):
        """Return structured NLP features for an interview answer."""

        cleaned_text = self.clean_text(text)
        tokens = self.tokenize(cleaned_text)
        keywords = self.extract_keywords(cleaned_text)
        skills = self.extract_skills(cleaned_text)
        stemmed_tokens = self.stem(text)
        lemmatized_tokens = self.lemmatize(text)
        sentiment = self.analyze_sentiment(text)

        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "tokens": tokens,
            "keywords": keywords,
            "skills": skills,
            "stemmed_tokens": stemmed_tokens,
            "lemmatized_tokens": lemmatized_tokens,
            "sentiment": sentiment,
            "word_count": len(tokens),
            "keyword_frequency": dict(Counter(keywords)),
            "is_empty": len(cleaned_text) == 0
        }
