
import random


class QuestionService:
    """Offline question bank with strict role and skill matching."""

    VALID_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}
    MAX_QUESTIONS = 10

    QUESTION_BANK = [
        # -------------------------------------------------
        # PYTHON DEVELOPER
        # -------------------------------------------------
        {
            "id": 1,
            "question": "What is a variable in Python?",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Beginner",
            "reference_answer": "A variable is a name that refers to a value or object. Python determines the type dynamically."
        },
        {
            "id": 2,
            "question": "What is the difference between a list and a tuple?",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Beginner",
            "reference_answer": "Lists are mutable, while tuples are immutable. Both can store multiple items."
        },
        {
            "id": 3,
            "question": "Explain decorators in Python.",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Intermediate",
            "reference_answer": "A decorator wraps a function or class to extend or modify its behavior without directly changing its code."
        },
        {
            "id": 4,
            "question": "How does a Python generator work?",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Intermediate",
            "reference_answer": "A generator yields values lazily, usually using yield, which can reduce memory usage for large sequences."
        },
        {
            "id": 5,
            "question": "Explain Python's Global Interpreter Lock.",
            "role": "python developer",
            "skills": ["python"],
            "difficulty": "Advanced",
            "reference_answer": "In conventional CPython builds, the GIL generally allows only one thread at a time to execute Python bytecode."
        },

        # -------------------------------------------------
        # MACHINE LEARNING ENGINEER
        # -------------------------------------------------
        {
            "id": 6,
            "question": "What is supervised machine learning?",
            "role": "machine learning engineer",
            "skills": ["machine learning", "ml", "python"],
            "difficulty": "Beginner",
            "reference_answer": "Supervised learning trains a model using labeled examples to predict outputs for new inputs."
        },
        {
            "id": 7,
            "question": "What is the difference between classification and regression?",
            "role": "machine learning engineer",
            "skills": ["machine learning", "ml"],
            "difficulty": "Beginner",
            "reference_answer": "Classification predicts categories, while regression predicts numerical values."
        },
        {
            "id": 8,
            "question": "Explain overfitting and how to reduce it.",
            "role": "machine learning engineer",
            "skills": ["machine learning", "ml"],
            "difficulty": "Intermediate",
            "reference_answer": "Overfitting occurs when a model learns training-specific patterns that do not generalize. Regularization, cross-validation and more data can help."
        },
        {
            "id": 9,
            "question": "Why might you choose a random forest over a single decision tree?",
            "role": "machine learning engineer",
            "skills": ["machine learning", "ml"],
            "difficulty": "Advanced",
            "reference_answer": "A random forest combines multiple randomized trees, often reducing variance and improving generalization."
        },

        # -------------------------------------------------
        # SOFTWARE DEVELOPER
        # -------------------------------------------------
        {
            "id": 10,
            "question": "What is a primary key in a database?",
            "role": "software developer",
            "skills": ["sql", "database"],
            "difficulty": "Beginner",
            "reference_answer": "A primary key uniquely identifies each row in a table and cannot contain NULL values."
        },
        {
            "id": 11,
            "question": "Explain the difference between WHERE and HAVING in SQL.",
            "role": "software developer",
            "skills": ["sql", "database"],
            "difficulty": "Intermediate",
            "reference_answer": "WHERE filters rows before grouping, while HAVING filters groups after GROUP BY."
        },
        {
            "id": 12,
            "question": "What is the difference between a process and a thread?",
            "role": "software developer",
            "skills": ["programming", "operating systems"],
            "difficulty": "Advanced",
            "reference_answer": "Processes have separate address spaces by default, while threads within a process share memory and resources."
        },

        # -------------------------------------------------
        # FRONTEND DEVELOPER
        # -------------------------------------------------
        {
            "id": 13,
            "question": "What is the difference between let, const, and var in JavaScript?",
            "role": "frontend developer",
            "skills": ["javascript", "js"],
            "difficulty": "Beginner",
            "reference_answer": "var is function-scoped, while let and const are block-scoped. let allows reassignment, whereas const prevents reassignment of the binding."
        },
        {
            "id": 14,
            "question": "What is the DOM in JavaScript?",
            "role": "frontend developer",
            "skills": ["javascript", "html5", "html", "dom"],
            "difficulty": "Beginner",
            "reference_answer": "The Document Object Model represents an HTML document as a tree of objects that JavaScript can access and modify."
        },
        {
            "id": 15,
            "question": "Explain the CSS box model.",
            "role": "frontend developer",
            "skills": ["css3", "css", "html5"],
            "difficulty": "Beginner",
            "reference_answer": "The CSS box model consists of content, padding, border, and margin."
        },
        {
            "id": 16,
            "question": "What is event delegation in JavaScript?",
            "role": "frontend developer",
            "skills": ["javascript", "js", "dom"],
            "difficulty": "Intermediate",
            "reference_answer": "Event delegation attaches one event listener to a parent element to handle events from its descendants using event bubbling."
        },
        {
            "id": 17,
            "question": "What is the difference between Flexbox and CSS Grid?",
            "role": "frontend developer",
            "skills": ["css3", "css"],
            "difficulty": "Intermediate",
            "reference_answer": "Flexbox is primarily a one-dimensional layout system, while CSS Grid handles two-dimensional layouts with rows and columns."
        },
        {
            "id": 18,
            "question": "How can you improve the performance of a frontend web application?",
            "role": "frontend developer",
            "skills": ["javascript", "html5", "css3"],
            "difficulty": "Advanced",
            "reference_answer": "Performance can be improved through code splitting, lazy loading, image optimization, caching and reducing unnecessary rendering."
        },

        # -------------------------------------------------
        # DEVOPS ENGINEER
        # -------------------------------------------------
        {
            "id": 19,
            "question": "What is Docker and why is it used?",
            "role": "devops engineer",
            "skills": ["docker"],
            "difficulty": "Beginner",
            "reference_answer": "Docker packages applications and their dependencies into containers, providing consistent environments."
        },
        {
            "id": 20,
            "question": "What is the difference between a Docker image and a container?",
            "role": "devops engineer",
            "skills": ["docker"],
            "difficulty": "Beginner",
            "reference_answer": "An image is a read-only template containing application files and dependencies. A container is an instance of that image."
        },
        {
            "id": 21,
            "question": "What is the purpose of Linux in DevOps?",
            "role": "devops engineer",
            "skills": ["linux"],
            "difficulty": "Beginner",
            "reference_answer": "Linux provides an operating system environment for servers, automation, scripting, process management and deployment."
        },
        {
            "id": 22,
            "question": "What is Infrastructure as Code?",
            "role": "devops engineer",
            "skills": ["terraform", "iac"],
            "difficulty": "Intermediate",
            "reference_answer": "Infrastructure as Code manages infrastructure through machine-readable configuration files, allowing repeatable and version-controlled provisioning."
        },
        {
            "id": 23,
            "question": "What is a CI/CD pipeline?",
            "role": "devops engineer",
            "skills": ["ci/cd", "docker", "aws"],
            "difficulty": "Intermediate",
            "reference_answer": "CI/CD automates integration, testing and delivery or deployment of software changes."
        },
        {
            "id": 24,
            "question": "How does Terraform manage infrastructure state?",
            "role": "devops engineer",
            "skills": ["terraform"],
            "difficulty": "Advanced",
            "reference_answer": "Terraform maintains a state file that maps configuration to real infrastructure resources and uses it to plan changes."
        },

        # -------------------------------------------------
        # BACKEND DEVELOPER
        # -------------------------------------------------
        {
            "id": 25,
            "question": "What is an API?",
            "role": "backend developer",
            "skills": ["api", "backend"],
            "difficulty": "Beginner",
            "reference_answer": "An API defines how software components communicate through a defined set of operations and data formats."
        },
        {
            "id": 26,
            "question": "What is the difference between GET and POST requests?",
            "role": "backend developer",
            "skills": ["api", "http", "backend"],
            "difficulty": "Beginner",
            "reference_answer": "GET retrieves a resource, while POST submits data for processing or resource creation."
        },
        {
            "id": 27,
            "question": "What is middleware in a backend application?",
            "role": "backend developer",
            "skills": ["backend", "api"],
            "difficulty": "Intermediate",
            "reference_answer": "Middleware processes requests or responses between the client and application route handlers."
        },
        {
            "id": 28,
            "question": "Explain authentication and authorization.",
            "role": "backend developer",
            "skills": ["backend", "security", "api"],
            "difficulty": "Intermediate",
            "reference_answer": "Authentication verifies identity, while authorization determines what an authenticated user is permitted to do."
        },
        {
            "id": 29,
            "question": "How would you design a scalable backend service?",
            "role": "backend developer",
            "skills": ["backend", "api", "database"],
            "difficulty": "Advanced",
            "reference_answer": "A scalable backend can use stateless services, caching, database optimization, load balancing, asynchronous processing and monitoring."
        },

        # -------------------------------------------------
        # FULL STACK DEVELOPER
        # -------------------------------------------------
        {
            "id": 30,
            "question": "What is React and why is it used?",
            "role": "full stack developer",
            "skills": ["react", "javascript"],
            "difficulty": "Beginner",
            "reference_answer": "React is a JavaScript library for building user interfaces using reusable components and declarative rendering."
        },
        {
            "id": 31,
            "question": "What is TypeScript and how is it different from JavaScript?",
            "role": "full stack developer",
            "skills": ["typescript", "javascript"],
            "difficulty": "Beginner",
            "reference_answer": "TypeScript is a superset of JavaScript that adds static type checking and compiles to JavaScript."
        },
        {
            "id": 32,
            "question": "How does a React frontend communicate with a backend API?",
            "role": "full stack developer",
            "skills": ["react", "javascript", "api", "backend"],
            "difficulty": "Intermediate",
            "reference_answer": "A React frontend can use fetch or Axios to send HTTP requests to backend API endpoints and process the returned data."
        },
        {
            "id": 33,
            "question": "Why is TypeScript useful in a large full stack application?",
            "role": "full stack developer",
            "skills": ["typescript", "react"],
            "difficulty": "Advanced",
            "reference_answer": "TypeScript provides static typing, better tooling, improved refactoring and earlier detection of type-related errors."
        },

        # -------------------------------------------------
        # DATA SCIENTIST
        # -------------------------------------------------
        {
            "id": 34,
            "question": "What is the difference between structured and unstructured data?",
            "role": "data scientist",
            "skills": ["python", "data analysis"],
            "difficulty": "Beginner",
            "reference_answer": "Structured data follows a defined schema, while unstructured data includes formats such as text, images and audio."
        },
        {
            "id": 35,
            "question": "What is data preprocessing?",
            "role": "data scientist",
            "skills": ["python", "pandas", "data analysis"],
            "difficulty": "Beginner",
            "reference_answer": "Data preprocessing cleans and transforms raw data by handling missing values, duplicates, inconsistent formats and other issues."
        },
        {
            "id": 36,
            "question": "What is feature engineering?",
            "role": "data scientist",
            "skills": ["python", "machine learning", "data analysis"],
            "difficulty": "Intermediate",
            "reference_answer": "Feature engineering creates or transforms input variables to improve the usefulness of data for machine learning models."
        },
        {
            "id": 37,
            "question": "How would you handle missing values in a dataset?",
            "role": "data scientist",
            "skills": ["python", "pandas", "data analysis"],
            "difficulty": "Advanced",
            "reference_answer": "Missing values can be handled by deletion, statistical imputation, model-based imputation or explicit missing-value indicators depending on the data."
        },

        # -------------------------------------------------
        # DATA ANALYST
        # -------------------------------------------------
        {
            "id": 38,
            "question": "What is the purpose of data visualization?",
            "role": "data analyst",
            "skills": ["data analysis", "tableau", "power bi"],
            "difficulty": "Beginner",
            "reference_answer": "Data visualization presents information graphically to reveal patterns, trends and comparisons."
        },
        {
            "id": 39,
            "question": "What is the difference between INNER JOIN and LEFT JOIN?",
            "role": "data analyst",
            "skills": ["sql", "database"],
            "difficulty": "Beginner",
            "reference_answer": "INNER JOIN returns matching rows from both tables, while LEFT JOIN returns all left-table rows and matching right-table rows."
        },
        {
            "id": 40,
            "question": "What is a KPI?",
            "role": "data analyst",
            "skills": ["data analysis", "tableau", "power bi"],
            "difficulty": "Intermediate",
            "reference_answer": "A Key Performance Indicator is a measurable value used to evaluate progress toward a defined objective."
        },
        {
            "id": 41,
            "question": "How would you identify outliers in a dataset?",
            "role": "data analyst",
            "skills": ["python", "sql", "data analysis"],
            "difficulty": "Advanced",
            "reference_answer": "Outliers can be identified using box plots, the interquartile range, z-scores and domain-specific thresholds."
        },

        # -------------------------------------------------
        # NLP ENGINEER
        # -------------------------------------------------
        {
            "id": 42,
            "question": "What is Natural Language Processing?",
            "role": "nlp engineer",
            "skills": ["nlp", "python"],
            "difficulty": "Beginner",
            "reference_answer": "Natural Language Processing is a field of AI that enables computers to process, analyze and generate human language."
        },
        {
            "id": 43,
            "question": "What is tokenization in NLP?",
            "role": "nlp engineer",
            "skills": ["nlp", "python"],
            "difficulty": "Beginner",
            "reference_answer": "Tokenization splits text into smaller units such as words, subwords or sentences."
        },
        {
            "id": 44,
            "question": "What is the difference between stemming and lemmatization?",
            "role": "nlp engineer",
            "skills": ["nlp", "python"],
            "difficulty": "Intermediate",
            "reference_answer": "Stemming removes word endings using heuristic rules, while lemmatization uses linguistic analysis to find a base dictionary form."
        },
        {
            "id": 45,
            "question": "What are word embeddings?",
            "role": "nlp engineer",
            "skills": ["nlp", "machine learning", "python"],
            "difficulty": "Advanced",
            "reference_answer": "Word embeddings represent words as dense numerical vectors that capture semantic or contextual relationships."
        },

        # -------------------------------------------------
        # GENERAL TECHNICAL
        # -------------------------------------------------
        {
            "id": 46,
            "question": "What is the difference between a compiler and an interpreter?",
            "role": "general",
            "skills": ["programming", "python", "javascript"],
            "difficulty": "Beginner",
            "reference_answer": "A compiler translates code before execution, while an interpreter executes instructions through an interpretation process."
        },
        {
            "id": 47,
            "question": "What is the purpose of version control?",
            "role": "general",
            "skills": ["git", "programming"],
            "difficulty": "Beginner",
            "reference_answer": "Version control tracks changes to files, supports collaboration and allows developers to restore earlier versions."
        },
        {
            "id": 48,
            "question": "What is the difference between SQL and NoSQL databases?",
            "role": "general",
            "skills": ["sql", "database"],
            "difficulty": "Intermediate",
            "reference_answer": "SQL databases typically use relational tables and schemas, while NoSQL databases support models such as documents, key-value pairs and graphs."
        },
        {
            "id": 49,
            "question": "Explain time and space complexity.",
            "role": "general",
            "skills": ["programming", "algorithms"],
            "difficulty": "Advanced",
            "reference_answer": "Time complexity describes how running time grows with input size, while space complexity describes how memory usage grows."
        },
    ]

    def __init__(self, question_bank=None, rng=None, client=None, model=None):
        self.question_bank = (
            list(question_bank)
            if question_bank is not None
            else list(self.QUESTION_BANK)
        )
        self.rng = rng or random.Random()

        # Kept for compatibility with existing application code.
        # Offline question selection does not use the API client.
        self.client = client
        self.model = model

    @staticmethod
    def _normalize(value):
        return str(value).strip().lower()

    def get_questions(
        self,
        role,
        skills=None,
        difficulty="Beginner",
        number_of_questions=5,
        exclude_ids=None,
    ):
        """Return role-specific questions without requiring an API."""

        if not isinstance(role, str) or not role.strip():
            raise ValueError("Role must not be empty.")

        if difficulty not in self.VALID_DIFFICULTIES:
            raise ValueError(
                "Difficulty must be Beginner, Intermediate, or Advanced."
            )

        if (
            not isinstance(number_of_questions, int)
            or isinstance(number_of_questions, bool)
            or number_of_questions < 1
        ):
            raise ValueError(
                "number_of_questions must be a positive integer."
            )

        if number_of_questions > self.MAX_QUESTIONS:
            raise ValueError(
                f"Only up to {self.MAX_QUESTIONS} questions can be requested."
            )

        if skills is None:
            skills = []

        requested_role = self._normalize(role)

        requested_skills = {
            self._normalize(skill)
            for skill in skills
            if isinstance(skill, str) and skill.strip()
        }

        excluded = {str(item) for item in (exclude_ids or [])}

        # Match role and skill aliases.
        skill_aliases = {
            "javascript": {"javascript", "js"},
            "js": {"javascript", "js"},
            "html5": {"html5", "html"},
            "html": {"html5", "html"},
            "css3": {"css3", "css"},
            "css": {"css3", "css"},
            "machine learning": {"machine learning", "ml"},
            "ml": {"machine learning", "ml"},
            "ci/cd": {"ci/cd", "cicd"},
            "cicd": {"ci/cd", "cicd"},
            "iac": {"iac", "terraform"},
            "terraform": {"terraform", "iac"},
        }

        expanded_skills = set(requested_skills)

        for skill in requested_skills:
            expanded_skills.update(skill_aliases.get(skill, set()))

<<<<<<< HEAD
        # First try to match both role and selected skills.
=======
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
        candidates = []

        for item in self.question_bank:
            if str(item.get("id")) in excluded:
                continue

            item_role = self._normalize(item.get("role", ""))

            # Exact role match, or an explicitly general question.
            if item_role != requested_role:
                continue

            item_skills = {
                self._normalize(skill)
                for skill in item.get("skills", [])
            }

            # General questions must also match a selected skill.
            if requested_skills and not item_skills.intersection(expanded_skills):
                continue

            # Do not use general questions as substitutes for unrelated skills.
            if not requested_skills and item_role == "general":
                continue

            candidates.append(item)

<<<<<<< HEAD
        # Fall back to role-only questions when too few skill-matched questions exist.
        if requested_skills and len(candidates) < number_of_questions:
            existing_ids = {str(item.get("id")) for item in candidates}

            for item in self.question_bank:
                if str(item.get("id")) in excluded or str(item.get("id")) in existing_ids:
                    continue

                item_role = self._normalize(item.get("role", ""))

                if item_role != requested_role:
                    continue

                # Skip general questions when specific skills were requested.
                if item_role == "general":
                    continue

                candidates.append(item)

                if len(candidates) >= number_of_questions:
                    break

=======
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
        # Prefer exact difficulty first.
        exact_difficulty = [
            item for item in candidates
            if item.get("difficulty") == difficulty
        ]

        other_difficulties = [
            item for item in candidates
            if item.get("difficulty") != difficulty
        ]

        self.rng.shuffle(exact_difficulty)
        self.rng.shuffle(other_difficulties)

        selected = exact_difficulty[:number_of_questions]

        if len(selected) < number_of_questions:
            remaining = number_of_questions - len(selected)
            selected.extend(other_difficulties[:remaining])

<<<<<<< HEAD
        # Return whatever questions are available rather than failing outright.
        # This keeps interviews runnable even when the local bank is sparse.
        if not selected:
            raise ValueError(
                f"No relevant offline questions are available for {role} "
                f"with the selected skills. Add more questions to the local bank."
=======
        # Never call the OpenAI API as a fallback.
        if len(selected) < number_of_questions:
            raise ValueError(
                f"Only {len(selected)} relevant offline questions are "
                f"available for {role} with the selected skills. "
                f"Available: {len(selected)}; requested: "
                f"{number_of_questions}. Add more questions to the local bank."
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
            )

        return [
            {
                "id": str(item["id"]),
                "question": item["question"],
                "role": item["role"],
                "skills": list(item.get("skills", [])),
                "difficulty": item["difficulty"],
                "reference_answer": item["reference_answer"],
            }
            for item in selected[:number_of_questions]
        ]
