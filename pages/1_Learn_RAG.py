import streamlit as st

st.set_page_config(page_title="Learn RAG", page_icon="🧠", layout="wide")

MODULES = [
    {
        "id": "01",
        "title": "What is RAG?",
        "subtitle": "Learn how an AI chatbot can answer from a document instead of guessing.",
        "intro": [
            "RAG stands for Retrieval-Augmented Generation. The name sounds technical, but the idea is simple: before the AI answers a question, it first looks for useful information in a trusted source such as a PDF, policy, guide, knowledge base, or database.",
            "Think of RAG as an AI assistant that is allowed to open the company handbook before answering you. The system searches the document, selects the most useful pieces, gives those pieces to the language model, and then the model writes the response. For QA, this is important because a wrong answer may come from bad search, missing evidence, or the final AI response.",
        ],
        "analogy_title": "Think of RAG like a librarian",
        "analogy": "You ask a librarian, ‘How long is a password reset link valid?’ The librarian does not invent an answer. They find the correct manual, locate the relevant paragraph, read it, and then answer you. RAG follows the same idea automatically.",
        "steps": [
            ("📄", "Trusted document", "The information we want the AI to use."),
            ("✂️", "Small pieces", "The document is divided into searchable sections."),
            ("🔎", "Find the best piece", "The system searches for information related to the question."),
            ("🧠", "AI reads evidence", "The LLM receives the useful document text."),
            ("💬", "Answer", "The AI answers using the evidence it received."),
        ],
        "concepts": [
            ("Knowledge source", "The trusted place where the answer should come from. In this course we mainly use PDFs, but real systems can also use websites, databases, support articles, product manuals, and internal company documents."),
            ("Retrieval", "The search step. The system tries to find the pieces of the document that are most relevant to the student's question. If retrieval is wrong, the LLM may never see the correct information."),
            ("Generation", "After retrieval, the language model writes a natural-language response. A good response should stay within the evidence instead of adding unsupported facts."),
            ("Grounding", "Grounding means the important claims in the answer can be supported by the retrieved source. QA testers compare the answer against the evidence instead of trusting how confident the chatbot sounds."),
        ],
        "examples": [
            {"label":"Example 1 — direct fact","source":"Password reset links expire after 30 minutes.","question":"How long is the password reset link valid?","evidence":"Password reset links expire after 30 minutes.","answer":"The password reset link is valid for 30 minutes.","result":"✅ Good: the answer matches the evidence."},
            {"label":"Example 2 — condition matters","source":"Items may be returned within 30 days only if they are unopened.","question":"Can I return an opened product after 20 days?","evidence":"Items may be returned within 30 days only if they are unopened.","answer":"No. The item must be unopened to qualify for the return policy.","result":"✅ Good: the answer includes the important condition."},
            {"label":"Example 3 — information is missing","source":"The document explains password reset and account recovery. It does not name the company CEO.","question":"Who is the company CEO?","evidence":"No supporting information found in the document.","answer":"I don't know based on the uploaded document.","result":"✅ Good: the AI does not invent an answer."},
        ],
        "failures": [
            ("Wrong evidence", "The system retrieves an unrelated paragraph, so the LLM receives bad context."),
            ("Missing condition", "The answer says ‘30 days’ but forgets ‘only if unopened’."),
            ("Hallucination", "The source has no answer, but the chatbot makes up a believable fact."),
        ],
        "questions": [
            ("What does RAG stand for?", "Retrieval-Augmented Generation."),
            ("Why does RAG search a document before answering?", "So the AI can answer from trusted, relevant information instead of relying only on general model knowledge."),
            ("If the final answer is wrong, did the LLM definitely fail?", "No. Retrieval may have returned the wrong evidence. QA should inspect the evidence before deciding the root cause."),
            ("What should the chatbot do if the PDF does not contain the answer?", "It should clearly say that the answer is not available from the provided document rather than inventing information."),
        ],
        "exercise": "A PDF says: ‘Employees receive 15 vacation days per year.’ The student asks: ‘Can I carry unused vacation days into next year?’ The PDF contains no carry-forward rule. What should a well-grounded RAG chatbot do?",
        "exercise_answer": "It should say that it cannot determine the carry-forward policy from the uploaded document. It should not guess yes or no.",
    },
    {
        "id": "02",
        "title": "RAG Architecture",
        "subtitle": "See the complete journey from document upload to final answer.",
        "intro": [
            "A RAG chatbot is not one single AI component. It is a pipeline made of several connected stages. Each stage has a specific job, and a problem in an early stage can create a bad answer at the end.",
            "For a QA tester, architecture matters because it helps with root-cause analysis. Instead of reporting only ‘the chatbot is wrong’, we can investigate whether the document was loaded correctly, split correctly, indexed correctly, retrieved correctly, or whether the final response added unsupported information.",
        ],
        "analogy_title": "Think of it like a restaurant order",
        "analogy": "A customer gives an order, the waiter records it, the kitchen finds ingredients, the chef prepares the food, and the waiter serves it. If the meal is wrong, the problem might be the order, ingredients, preparation, or delivery. RAG has the same kind of pipeline.",
        "steps": [
            ("📥", "Loader", "Reads the PDF or knowledge source."),
            ("✂️", "Chunker", "Breaks long text into manageable pieces."),
            ("🔢", "Embedding", "Represents the meaning of each piece numerically."),
            ("🗂️", "Index", "Stores searchable representations."),
            ("🔎", "Retriever", "Chooses the best pieces for the question."),
            ("🧠", "LLM", "Writes the answer using retrieved context."),
        ],
        "concepts": [
            ("Loader", "Reads the source and extracts usable text. If a scanned PDF contains no readable text, everything after this stage may fail."),
            ("Chunker", "Splits large text into smaller sections so they can be searched. Bad boundaries can separate a rule from its condition or exception."),
            ("Embedding + index", "The system creates searchable numeric representations of the chunks and stores them. This allows meaning-based search instead of only exact word matching."),
            ("Retriever", "Receives the user's question and selects the chunks that appear most useful. Retrieval is one of the most important areas for RAG QA."),
            ("Prompt + LLM", "The retrieved evidence is placed into the prompt and sent to the model. The model should answer from that context and avoid adding unsupported information."),
        ],
        "examples": [
            {"label":"Example 1 — healthy pipeline","source":"Return policy: unopened items can be returned within 30 days.","question":"Can I return an unopened item after 20 days?","evidence":"unopened items can be returned within 30 days","answer":"Yes. An unopened item is within the 30-day return window.","result":"✅ Loader, retrieval, and answer all worked."},
            {"label":"Example 2 — retrieval failure","source":"Correct policy exists in the PDF: reset links expire after 30 minutes.","question":"When does my reset link expire?","evidence":"Office support hours are 9 AM to 5 PM.","answer":"Support is available from 9 AM to 5 PM.","result":"❌ Root cause starts at retrieval: wrong evidence reached the model."},
            {"label":"Example 3 — generation failure","source":"Correct evidence says the link expires after 30 minutes.","question":"When does my reset link expire?","evidence":"Reset links expire after 30 minutes.","answer":"The link expires after 60 minutes.","result":"❌ Retrieval is correct, but the final answer contradicts it."},
        ],
        "failures": [("Load failure","Text never becomes searchable."),("Retrieval failure","Correct content exists but is not selected."),("Generation failure","Correct evidence is selected but answer changes or invents a fact.")],
        "questions": [
            ("Why should QA understand the architecture?", "Because the same wrong final answer can be caused by different stages, and good defect investigation identifies where the failure began."),
            ("What does the retriever do?", "It chooses the chunks that appear most relevant to the user's question."),
            ("If evidence is correct but the answer is wrong, where is the likely problem?", "The generation/prompt/LLM stage should be investigated because retrieval supplied the right context."),
            ("If evidence is unrelated, what should QA inspect first?", "Retrieval, indexing, embeddings, and the source/chunk setup before blaming the LLM."),
        ],
        "exercise": "The PDF definitely contains the correct refund policy. The chatbot answers incorrectly, and the evidence panel shows an unrelated shipping paragraph. Which stage failed first, and why?",
        "exercise_answer": "Retrieval failed first because the system selected irrelevant evidence. The final answer may also be bad, but QA should start with the retrieval problem.",
    },
    {
        "id": "03",
        "title": "Chunking",
        "subtitle": "Understand why long documents are split and how bad splits create missing context.",
        "intro": [
            "A long PDF may contain hundreds of paragraphs. Instead of searching the whole document every time, RAG systems usually divide it into smaller pieces called chunks. Retrieval searches these chunks and sends only the most useful ones to the model.",
            "Chunking sounds simple, but it can change the meaning of the information. If a rule is in one chunk and its exception is pushed into another, the chatbot may retrieve only half of the story. QA should therefore test questions that depend on conditions, exceptions, lists, tables, and information near section boundaries.",
        ],
        "analogy_title": "Think of cutting a recipe into cards",
        "analogy": "If one card says ‘Bake for 30 minutes’ and the next card says ‘only at 180°C’, reading only the first card gives an incomplete instruction. Chunking must keep related meaning together whenever possible.",
        "steps": [("📄","Long document","Many sections and topics."),("✂️","Chunk 1","One meaningful section."),("↔️","Overlap","A little shared text keeps context."),("✂️","Chunk 2","Next meaningful section."),("🔎","Search","Retriever selects useful chunks.")],
        "concepts": [
            ("Chunk", "A smaller piece of a large document. Good chunks are large enough to preserve meaning but focused enough to be relevant."),
            ("Chunk size", "How much text goes into one chunk. Very small chunks may lose context; very large chunks may contain too many unrelated ideas."),
            ("Overlap", "Some text is repeated between neighboring chunks. This can preserve context when important information sits near a boundary."),
            ("Boundary problem", "A rule, condition, exception, heading, or table row can be separated from the text it belongs to. This is a common source of incomplete RAG answers."),
        ],
        "examples": [
            {"label":"Good chunk","source":"Items may be returned within 30 days only if unopened.","question":"Can I return an opened item after 10 days?","evidence":"Items may be returned within 30 days only if unopened.","answer":"No. The policy requires the item to be unopened.","result":"✅ Rule and condition stayed together."},
            {"label":"Bad split","source":"Chunk A: Items may be returned within 30 days. Chunk B: Only unopened items are eligible.","question":"How long do I have to return an item?","evidence":"Chunk A only: Items may be returned within 30 days.","answer":"You can return an item within 30 days.","result":"⚠️ Incomplete: the unopened condition was lost."},
            {"label":"Two-chunk question","source":"Vacation: 15 days yearly. Unused days cannot be carried forward unless a manager approves an exception.","question":"Can unused vacation be carried forward?","evidence":"Unused days cannot be carried forward unless a manager approves an exception.","answer":"Normally no, unless a manager approves an exception.","result":"✅ The retrieved chunk contains the rule and exception."},
        ],
        "failures": [("Too small","Context gets separated."),("Too large","Search becomes noisy and less focused."),("Bad boundary","Important condition or exception lands in another chunk.")],
        "questions": [
            ("Why not keep the entire PDF as one chunk?", "A huge chunk contains many unrelated topics, making search noisy and wasting model context."),
            ("What happens if chunks are too small?", "The answer may require information that has been split across multiple chunks, so retrieval may return only part of the meaning."),
            ("Why use overlap?", "Overlap repeats some text between neighboring chunks to reduce context loss at boundaries."),
            ("What is a useful QA test for chunking?", "Ask questions that depend on a rule plus its condition, exception, heading, or neighboring sentence."),
        ],
        "exercise": "A policy says: ‘Employees may work remotely two days per week. New employees must complete their first 90 days in the office.’ Why would splitting these two sentences into unrelated chunks be risky?",
        "exercise_answer": "Because retrieving only the first sentence could incorrectly suggest that every employee can immediately work remotely. The 90-day condition changes the rule for new employees.",
    },
    {
        "id": "04",
        "title": "Embeddings",
        "subtitle": "Learn how RAG can search by meaning even when the words are different.",
        "intro": [
            "People rarely ask questions using the exact words found in a document. A policy might say ‘recover account access’, while a user asks ‘How do I reset my password?’ Embeddings help the system recognize that these phrases are related in meaning.",
            "An embedding is simply a numeric representation of meaning. You do not need the mathematics to test it. For QA, the practical idea is that similar meanings should be treated as close, while unrelated meanings should stay far apart.",
        ],
        "analogy_title": "Think of a map of meanings",
        "analogy": "Imagine every sentence is placed on a map. ‘Reset my password’ and ‘recover account access’ should appear close together. ‘Change my profile photo’ should appear far away. Embeddings create that kind of meaning map using numbers.",
        "steps": [("💬","User wording","How do I reset my password?"),("🔢","Embedding","Turn meaning into numbers."),("📍","Meaning map","Compare with document chunks."),("🎯","Closest meaning","Recover account access using email."),("🔎","Retrieve","Send that chunk to the LLM.")],
        "concepts": [
            ("Embedding", "A list of numbers representing the semantic meaning of text. The numbers are used for comparison and search, not shown directly to the user."),
            ("Semantic similarity", "Two pieces of text can be similar even when they use different words. This is what allows paraphrases and synonyms to work."),
            ("Similarity score", "The system calculates how close the question is to each stored chunk. Higher similarity usually means a better retrieval candidate."),
            ("QA focus", "Test paraphrases, synonyms, similar-but-wrong topics, abbreviations, and ambiguous wording to see whether semantic search behaves sensibly."),
        ],
        "examples": [
            {"label":"Same meaning, different words","source":"Users can recover account access using their registered email.","question":"How do I reset my password?","evidence":"Users can recover account access using their registered email.","answer":"Use your registered email to recover account access.","result":"✅ Semantic matching worked without exact keyword duplication."},
            {"label":"Synonym test","source":"Employees may purchase equipment with manager authorization.","question":"Do I need my manager's approval to buy equipment?","evidence":"Employees may purchase equipment with manager authorization.","answer":"Yes. Manager authorization is required.","result":"✅ ‘approval’ matched the meaning of ‘authorization’."},
            {"label":"Similar but wrong topic","source":"Password reset links expire after 30 minutes. Session timeout occurs after 15 minutes.","question":"How long does the password reset link last?","evidence":"Session timeout occurs after 15 minutes.","answer":"15 minutes.","result":"❌ Search confused two time-based security concepts."},
        ],
        "failures": [("Paraphrase miss","Different wording does not retrieve the correct chunk."),("Semantic confusion","Similar topics are mixed up."),("Ambiguity","A short question matches multiple meanings and retrieves the wrong one.")],
        "questions": [
            ("Do embeddings generate the final answer?", "No. They help search for relevant text. The LLM still generates the response."),
            ("Why are embeddings useful compared with keyword search?", "They can match similar meanings even when the user and document use different words."),
            ("What is a simple embeddings QA test?", "Ask the same intent using several paraphrases and verify that the correct evidence remains highly ranked."),
            ("What is a tricky negative test?", "Use two topics with similar words or concepts and verify the system selects the correct one."),
        ],
        "exercise": "Which document sentence should be closest in meaning to the question ‘How long is my reset link valid?’ A) Reset links expire after 30 minutes. B) Support opens at 9 AM. C) You can change your profile photo in Settings.",
        "exercise_answer": "A. It expresses the same meaning as the question, even though the wording is slightly different.",
    },
    {
        "id": "05",
        "title": "Vector Search & Retrieval",
        "subtitle": "See how the system ranks chunks and chooses evidence for the LLM.",
        "intro": [
            "After embeddings are created, the system can compare the user's question with stored chunks and rank them by similarity. The highest-ranked chunks become the retrieved context sent to the model.",
            "This stage is critical for QA because the LLM cannot use evidence it never receives. A document can contain the perfect answer, but if that chunk ranks too low, the final response may still be wrong.",
        ],
        "analogy_title": "Think of search results",
        "analogy": "When you search the web, the most relevant results should appear near the top. Vector retrieval works similarly, but it ranks pieces of your private knowledge source by semantic similarity to the question.",
        "steps": [("❓","Question","When does the reset link expire?"),("🔢","Query embedding","Represent question meaning."),("📊","Rank chunks","Compare against stored chunks."),("🥇","Top-K","Select the best few results."),("🧠","LLM context","Pass selected evidence to the model.")],
        "concepts": [
            ("Vector search", "Meaning-based search over embedded chunks. It tries to find chunks close to the question in semantic space."),
            ("Top-K", "How many of the highest-ranked chunks are returned. For example, Top-K = 4 means the four strongest candidates are sent forward."),
            ("Relevance", "A relevant chunk helps answer the actual question. QA should judge retrieved evidence independently from the final answer."),
            ("Retrieval failure", "The correct content exists but is not returned, irrelevant chunks are returned, or correct chunks are ranked below less useful ones."),
        ],
        "examples": [
            {"label":"Ranking works","source":"A: reset link 30 minutes | B: support hours 9–5 | C: profile photo settings","question":"When does my password reset link expire?","evidence":"A: Reset link expires after 30 minutes.","answer":"After 30 minutes.","result":"✅ Correct chunk ranked highest."},
            {"label":"Correct chunk misses Top-K","source":"Correct answer is stored in Chunk 4, but Top-K is set to 2.","question":"What is the remote-work probation rule?","evidence":"Only Chunks 1 and 2 are returned, neither contains the rule.","answer":"I don't know based on the uploaded document.","result":"⚠️ Safe answer, but retrieval still failed because the document actually contains the information."},
            {"label":"Irrelevant evidence ranked first","source":"The document contains password reset and session timeout rules.","question":"How long is the reset link valid?","evidence":"Session timeout is 15 minutes.","answer":"15 minutes.","result":"❌ Retrieval selected a related but incorrect security rule."},
        ],
        "failures": [("Correct chunk missing","Relevant content does not appear in Top-K."),("Wrong ranking","Less relevant content appears above the correct chunk."),("Noise","Too many weak chunks make the final context confusing.")],
        "questions": [
            ("What does Top-K mean?", "The number of highest-ranked chunks returned to the LLM."),
            ("What should QA inspect first when a response is wrong?", "Inspect the retrieved evidence to determine whether the model received the right context."),
            ("Can retrieval fail even when the PDF contains the answer?", "Yes. The correct chunk may be ranked below the Top-K cutoff or confused with a similar topic."),
            ("How can QA record retrieval quality?", "Label each returned chunk as relevant, partially relevant, or irrelevant and note whether the correct answer-bearing chunk was present."),
        ],
        "exercise": "Top-K is 2. The correct answer-bearing chunk ranks 4th. What is the QA problem even if the bot safely says ‘I don't know’?",
        "exercise_answer": "Retrieval recall failed. The source contains the answer, but the retriever did not include it in the context given to the model.",
    },
    {
        "id": "06",
        "title": "Grounding & Hallucination",
        "subtitle": "Learn to prove whether an AI answer is actually supported by evidence.",
        "intro": [
            "AI answers can sound polished and confident even when they are wrong. Grounding gives QA a concrete way to evaluate them: compare every important claim in the response against the retrieved or source evidence.",
            "A grounded answer stays within the evidence. A partially grounded answer mixes supported information with missing or unsupported details. A hallucinated answer invents information that the source does not support.",
        ],
        "analogy_title": "Think of an open-book exam",
        "analogy": "The chatbot is allowed to answer only from the pages placed on its desk. If it writes a fact that is not on those pages, it has gone beyond the evidence—just like a student claiming something they cannot show in the textbook.",
        "steps": [("📚","Evidence","What the system actually retrieved."),("💬","Answer","Claims made by the chatbot."),("⚖️","Compare","Can each important claim be traced to evidence?"),("✅","Grounded","Everything important is supported."),("❌","Hallucinated","One or more important facts are invented.")],
        "concepts": [
            ("Grounded", "All important claims are supported by the provided evidence. Wording can be different as long as the meaning remains faithful."),
            ("Partially grounded", "Some of the answer is supported, but an important condition, number, reason, or additional claim is missing support."),
            ("Hallucination", "The model invents or changes a fact that is not supported by the evidence. Fluency does not make it correct."),
            ("Out-of-scope", "The source simply does not contain the requested information. The safest behavior is to acknowledge that limitation rather than guess."),
        ],
        "examples": [
            {"label":"Grounded answer","source":"Returns are accepted within 30 days if unopened.","question":"Can an unopened item be returned after 20 days?","evidence":"Returns are accepted within 30 days if unopened.","answer":"Yes. An unopened item can be returned within the 30-day window.","result":"✅ Every important claim is supported."},
            {"label":"Partially grounded answer","source":"Returns are accepted within 30 days if unopened.","question":"What is the return policy?","evidence":"Returns are accepted within 30 days if unopened.","answer":"Returns are accepted within 30 days.","result":"⚠️ Partially grounded/incomplete: the unopened condition was omitted."},
            {"label":"Hallucination","source":"Returns are accepted within 30 days.","question":"How long do refunds take to reach my bank?","evidence":"Returns are accepted within 30 days.","answer":"Refunds arrive in 10 business days.","result":"❌ Hallucination: refund-processing time is not supported."},
        ],
        "failures": [("Invented number","A time, amount, or percentage appears without support."),("Missing condition","Answer is technically related but changes meaning by dropping an exception."),("False certainty","The bot gives a definite answer when the document contains no answer.")],
        "questions": [
            ("Is a confident answer necessarily correct?", "No. Confidence, grammar, and fluency do not prove grounding."),
            ("How does QA prove a hallucination?", "Identify the claim in the answer and show that the retrieved/source evidence does not support that claim."),
            ("What should happen for an out-of-scope question?", "The chatbot should state that the answer is not available from the provided source rather than fabricate a response."),
            ("Can an answer be partly correct and still fail?", "Yes. Missing an important condition or adding one unsupported fact can make the answer partially grounded or incorrect."),
        ],
        "exercise": "Evidence says only: ‘Employees receive a $500 yearly learning allowance.’ The chatbot says: ‘Employees receive $500 and must spend it before September 30.’ How should QA classify this?",
        "exercise_answer": "Partially grounded with a hallucinated detail. The $500 amount is supported, but the September 30 deadline is not in the evidence.",
    },
    {
        "id": "07",
        "title": "RAG Testing + Final AI QA Project",
        "subtitle": "Turn everything you learned into professional AI QA test cases and defects.",
        "intro": [
            "The goal of this course is not to memorize AI terminology. The goal is to test a real RAG application in a disciplined QA way: design test scenarios, execute prompts, inspect evidence, compare expected and actual behavior, and document defects clearly.",
            "In the final project you will use DocPilotAI as your system under test. You will upload a PDF, create a balanced set of test cases, intentionally look for retrieval and grounding failures, log reproducible defects, and review your QA score.",
        ],
        "analogy_title": "Think like a detective, not a chatbot user",
        "analogy": "A normal user asks a question and reads the answer. A QA engineer asks: What did I expect? What evidence should have been retrieved? What actually happened? Where did the failure begin? Can I reproduce it? That investigation mindset is the project.",
        "steps": [("📄","Upload PDF","Choose a text-based source."),("🧪","Design tests","Happy path, negative, retrieval, grounding, robustness."),("❓","Execute prompts","Ask the agent and capture results."),("🔎","Inspect evidence","Decide whether retrieval worked."),("🐞","Log defects","Expected vs actual + steps + severity."),("📊","Review score","Export your final QA evidence.")],
        "concepts": [
            ("Happy path", "A clear in-scope question whose answer exists in the source. This proves the basic RAG workflow can succeed."),
            ("Negative / out-of-scope", "A question intentionally not answered by the document. The expected behavior is a safe refusal or limitation, not invention."),
            ("Retrieval test", "Checks whether the correct evidence was selected. A final answer alone is not enough to judge retrieval."),
            ("Grounding test", "Checks whether every important answer claim is supported by evidence and whether conditions or exceptions were preserved."),
            ("Robustness test", "Uses paraphrases, ambiguous wording, edge cases, or challenging prompts to see whether behavior remains reliable."),
            ("Defect report", "A clear, reproducible record containing the exact prompt, expected behavior, actual behavior, evidence, severity, and steps."),
        ],
        "examples": [
            {"label":"Happy-path test","source":"Policy says reset links expire after 30 minutes.","question":"How long is my reset link valid?","evidence":"Reset links expire after 30 minutes.","answer":"30 minutes.","result":"PASS — correct retrieval and grounded answer."},
            {"label":"Negative test","source":"PDF contains no CEO information.","question":"Who is the CEO?","evidence":"No supporting evidence.","answer":"I don't know based on the uploaded document.","result":"PASS — safe out-of-scope handling."},
            {"label":"Defect candidate","source":"Correct rule says unopened items only.","question":"Can I return an opened item within 10 days?","evidence":"Returns within 30 days if unopened.","answer":"Yes, because it is within 30 days.","result":"FAIL — answer ignored a required condition; log a grounding defect."},
        ],
        "failures": [("Retrieval defect","Correct content is not selected."),("Grounding defect","Answer contradicts or goes beyond evidence."),("Robustness defect","Small wording changes produce inconsistent behavior.")],
        "questions": [
            ("What should every AI QA test case record?", "Scenario, prompt/input, expected behavior, actual behavior, PASS/FAIL, and useful evidence/notes."),
            ("Why include negative tests?", "They verify that the system does not invent answers when the knowledge source lacks information."),
            ("Why inspect evidence before logging a defect?", "It helps separate retrieval failures from generation/grounding failures and produces a better root-cause description."),
            ("What makes a strong AI bug report?", "Exact prompt, reproducible steps, expected result, actual result, evidence, severity, and a clear description of what failed."),
        ],
        "exercise": "Design five starter tests for one PDF: 1 happy path, 1 out-of-scope, 1 retrieval-focused, 1 grounding-focused, and 1 paraphrase/robustness test. For each, write the expected behavior before executing it.",
        "exercise_answer": "A complete set has one test in each category and records prompt, expected answer/behavior, expected evidence, actual answer, actual evidence, PASS/FAIL, and notes.",
    },
]

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 7% 0%,rgba(99,102,241,.10),transparent 27%),radial-gradient(circle at 96% 2%,rgba(14,165,233,.10),transparent 22%),#f8fafc;}
.block-container{max-width:1240px;padding-top:1.1rem;padding-bottom:3rem}
/* Hide the legacy main app entry so Learn RAG is visually first in the sidebar. */
section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] ul li:first-child{display:none!important}
.hero{background:linear-gradient(135deg,#0f172a 0%,#172554 52%,#312e81 100%);border-radius:26px;padding:30px 32px;color:white;box-shadow:0 20px 46px rgba(15,23,42,.17);margin-bottom:18px}
.hero h1{margin:0;font-size:34px;letter-spacing:-.025em}.hero p{color:#dbeafe;font-size:16px;line-height:1.6;max-width:900px;margin:8px 0 0}.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}.chip{padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.14);font-size:12px;font-weight:750}
.lesson-head{background:#fff;border:1px solid #e2e8f0;border-radius:20px;padding:20px 22px;margin:14px 0;box-shadow:0 7px 22px rgba(15,23,42,.045)}.kicker{font-size:12px;font-weight:900;color:#4f46e5;text-transform:uppercase;letter-spacing:.09em}.lesson-title{font-size:26px;font-weight:900;color:#0f172a;margin:4px 0}.lesson-sub{font-size:15px;color:#64748b;line-height:1.55}
.prose{font-size:16px;line-height:1.75;color:#334155}.prose p{margin:.3rem 0 .9rem}.analogy{background:linear-gradient(135deg,#fff7ed,#fffbeb);border:1px solid #fed7aa;border-radius:18px;padding:19px 21px;margin:15px 0}.analogy-title{font-size:18px;font-weight:850;color:#9a3412;margin-bottom:6px}.analogy-copy{font-size:15px;line-height:1.65;color:#7c2d12}
.diagram{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:11px;margin:15px 0 22px}.node{background:linear-gradient(145deg,#0f172a,#1e293b);border:1px solid #334155;color:#fff;border-radius:18px;padding:18px 14px;min-height:128px;text-align:center;box-shadow:0 9px 22px rgba(15,23,42,.11)}.node-icon{font-size:28px}.node-title{font-size:15px;font-weight:850;margin:8px 0 5px}.node-copy{font-size:12px;color:#cbd5e1;line-height:1.45}
.concept-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px;margin:12px 0 22px}.concept{background:white;border:1px solid #e2e8f0;border-radius:17px;padding:18px;box-shadow:0 5px 17px rgba(15,23,42,.04)}.concept b{font-size:15px;color:#0f172a}.concept p{font-size:14px;line-height:1.6;color:#64748b;margin:7px 0 0}
.example-card{background:#fff;border:1px solid #dbe4f0;border-radius:20px;overflow:hidden;margin:14px 0;box-shadow:0 7px 20px rgba(15,23,42,.045)}.example-title{background:#eef2ff;padding:12px 17px;font-weight:850;color:#3730a3}.example-body{display:grid;grid-template-columns:1fr 1fr;gap:0}.example-cell{padding:15px 17px;border-top:1px solid #edf1f6}.example-cell:nth-child(odd){border-right:1px solid #edf1f6}.label{font-size:11px;text-transform:uppercase;letter-spacing:.06em;font-weight:850;color:#64748b}.value{font-size:14px;line-height:1.55;color:#1e293b;margin-top:4px}.example-result{padding:12px 17px;background:#f8fafc;border-top:1px solid #edf1f6;font-size:14px;font-weight:750;color:#334155}
.failure-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px}.failure{background:#fff1f2;border:1px solid #fecdd3;border-radius:16px;padding:16px}.failure b{color:#9f1239}.failure div{color:#881337;font-size:13px;line-height:1.5;margin-top:5px}.qa{background:#ecfeff;border-left:4px solid #06b6d4;border-radius:15px;padding:16px 18px;font-size:14px;line-height:1.8;color:#164e63}
.course-path{display:grid;grid-template-columns:repeat(7,minmax(95px,1fr));gap:7px;margin:10px 0 20px}.path-node{background:white;border:1px solid #e2e8f0;border-radius:14px;padding:11px 8px;text-align:center;font-size:11px;font-weight:800;color:#334155}.path-node strong{display:block;color:#4f46e5;font-size:12px;margin-bottom:3px}
.stTabs [data-baseweb="tab-list"]{gap:7px;background:#eaf0f7;padding:6px;border-radius:14px}.stTabs [data-baseweb="tab"]{border-radius:10px;height:44px;font-weight:760}.stTabs [aria-selected="true"]{background:white!important}.stButton>button{border-radius:12px;font-weight:750}div[data-testid="stExpander"]{border-radius:14px!important;border:1px solid #e2e8f0!important;background:white}
@media(max-width:800px){.concept-grid,.example-body{grid-template-columns:1fr}.example-cell:nth-child(odd){border-right:none}.failure-grid{grid-template-columns:1fr}.course-path{grid-template-columns:repeat(2,1fr)}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🧠 Learn RAG for AI Quality Assurance</h1>
  <p>No AI engineering background is required. We start with a simple everyday explanation, show the idea visually, walk through real examples, and then connect each concept to what a QA tester should validate.</p>
  <div class="chips"><span class="chip">Beginner friendly</span><span class="chip">Visual learning</span><span class="chip">Real examples</span><span class="chip">QA investigation</span><span class="chip">Final DocPilotAI project</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Your learning journey")
path_titles = [("01","RAG"),("02","Architecture"),("03","Chunking"),("04","Embeddings"),("05","Retrieval"),("06","Grounding"),("07","Project")]
st.markdown('<div class="course-path">' + ''.join(f'<div class="path-node"><strong>{n}</strong>{t}</div>' for n,t in path_titles) + '</div>', unsafe_allow_html=True)

labels = [f"{m['id']} — {m['title']}" for m in MODULES]
selected = st.selectbox("Choose module", labels, index=0)
module = MODULES[labels.index(selected)]

st.markdown(f"<div class='lesson-head'><div class='kicker'>Module {module['id']}</div><div class='lesson-title'>{module['title']}</div><div class='lesson-sub'>{module['subtitle']}</div></div>", unsafe_allow_html=True)

learn_tab, visual_tab, questions_tab, exercise_tab = st.tabs(["📘 Learn", "👀 Visual Examples", "❓ Questions & Answers", "🧪 Exercise"])

with learn_tab:
    st.markdown("## Start with the idea")
    st.markdown('<div class="prose">' + ''.join(f'<p>{p}</p>' for p in module['intro']) + '</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='analogy'><div class='analogy-title'>💡 {module['analogy_title']}</div><div class='analogy-copy'>{module['analogy']}</div></div>", unsafe_allow_html=True)

    st.markdown("## See how it works")
    diagram = '<div class="diagram">'
    for icon,title,copy in module['steps']:
        diagram += f'<div class="node"><div class="node-icon">{icon}</div><div class="node-title">{title}</div><div class="node-copy">{copy}</div></div>'
    diagram += '</div>'
    st.markdown(diagram, unsafe_allow_html=True)

    st.markdown("## Key concepts — in plain language")
    concept_html = '<div class="concept-grid">'
    for name, explanation in module['concepts']:
        concept_html += f'<div class="concept"><b>{name}</b><p>{explanation}</p></div>'
    concept_html += '</div>'
    st.markdown(concept_html, unsafe_allow_html=True)

    st.markdown("## What can go wrong?")
    failure_html = '<div class="failure-grid">'
    for name, explanation in module['failures']:
        failure_html += f'<div class="failure"><b>⚠️ {name}</b><div>{explanation}</div></div>'
    failure_html += '</div>'
    st.markdown(failure_html, unsafe_allow_html=True)

    st.markdown("## QA mindset")
    qa_lines = {
        "01":["Check whether the system found the right evidence.","Compare the final answer against that evidence.","Test what happens when the source does not contain the answer."],
        "02":["Trace the failure back through the pipeline instead of blaming the chatbot immediately.","Separate retrieval problems from answer-generation problems.","Capture evidence in defect reports so the root cause is clear."],
        "03":["Test rules with conditions and exceptions.","Test information near section boundaries.","Look for incomplete answers caused by missing neighboring context."],
        "04":["Ask the same question using different wording.","Test synonyms and similar-but-wrong topics.","Look for semantic confusion, not only keyword failures."],
        "05":["Inspect Top-K evidence before judging the answer.","Check whether the correct answer-bearing chunk is present.","Rate returned chunks as relevant, partially relevant, or irrelevant."],
        "06":["Trace each important answer claim to evidence.","Flag unsupported numbers, conditions, names, dates, or explanations.","Test safe handling when evidence is missing."],
        "07":["Write expected behavior before execution.","Record answer quality and evidence quality separately.","Create reproducible defects with exact prompts and evidence."],
    }
    st.markdown('<div class="qa">' + '<br>'.join('✅ '+x for x in qa_lines[module['id']]) + '</div>', unsafe_allow_html=True)

with visual_tab:
    st.markdown("## Walk through real examples")
    st.caption("Do not judge only the chatbot answer. Read the source, question, retrieved evidence, and result together.")
    for ex in module['examples']:
        st.markdown(f"""
        <div class="example-card">
          <div class="example-title">{ex['label']}</div>
          <div class="example-body">
            <div class="example-cell"><div class="label">📚 Source</div><div class="value">{ex['source']}</div></div>
            <div class="example-cell"><div class="label">❓ User question</div><div class="value">{ex['question']}</div></div>
            <div class="example-cell"><div class="label">🔎 Retrieved evidence</div><div class="value">{ex['evidence']}</div></div>
            <div class="example-cell"><div class="label">💬 Agent answer</div><div class="value">{ex['answer']}</div></div>
          </div>
          <div class="example-result">{ex['result']}</div>
        </div>
        """, unsafe_allow_html=True)

with questions_tab:
    st.markdown("## Check your understanding")
    st.write("Try to explain the answer in your own words before opening each panel. These are discussion questions for class, not memorization questions.")
    for i,(q,a) in enumerate(module['questions'],1):
        with st.expander(f"Q{i}. {q}"):
            st.success(a)
            st.caption("Ask yourself: how would I prove this during testing?")

with exercise_tab:
    st.markdown("## Small QA exercise")
    st.info(module['exercise'])
    student_answer = st.text_area("Your answer / reasoning", placeholder="Write what you think should happen and why...", key=f"student_answer_{module['id']}", height=120)
    if st.button("Show suggested answer", key=f"show_{module['id']}"):
        st.success(module['exercise_answer'])
    st.markdown("### Explain it like a QA tester")
    st.write("Before moving on, be able to explain **what the system should do, what could fail, and what evidence you would collect to prove the failure.**")

st.divider()
if module['id'] == '07':
    st.markdown("## 🚀 Final Project — DocPilotAI")
    st.write("Now use the real agent as your system under test. Upload a PDF, design test cases, execute prompts, inspect evidence, log defects, review your QA score, and export the final report.")
    if st.button("🚀 Start AI QA Project", type="primary", use_container_width=True):
        st.session_state['open_ai_qa_project'] = True
        st.switch_page('app.py')
else:
    next_no = int(module['id']) + 1
    st.caption(f"When you can explain this module in your own words, continue to Module {next_no:02d}.")
