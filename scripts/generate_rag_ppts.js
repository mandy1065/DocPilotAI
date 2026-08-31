const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

const outDir = path.join(process.cwd(), 'learning');
fs.mkdirSync(outDir, { recursive: true });

const modules = [
  {
    file: 'module_01_what_is_rag.pptx', title: 'Module 01 — What is RAG?', subtitle: 'Retrieval-Augmented Generation for QA students',
    slides: [
      ['Why this matters', ['LLMs do not automatically know your private PDF.', 'RAG lets an AI system retrieve document evidence before answering.', 'QA must test both the answer and the evidence used.'], 'LLM + document = grounded answer'],
      ['LLM vs RAG', ['LLM alone answers from model knowledge.', 'RAG retrieves relevant document chunks first.', 'The model then answers using retrieved context.'], 'Question → Retriever → Evidence → LLM → Answer'],
      ['Simple RAG flow', ['1. Upload document', '2. Split into chunks', '3. Create embeddings', '4. Retrieve top matching chunks', '5. Generate answer'], 'PDF → Chunks → Embeddings → Search → Answer'],
      ['What can go wrong?', ['Wrong chunk retrieved', 'Important evidence missing', 'Unsupported details added', 'Out-of-scope question answered confidently'], 'Bad retrieval → Bad answer'],
      ['QA perspective', ['Check correctness.', 'Check grounding.', 'Check negative/out-of-scope behavior.', 'Record expected vs actual with evidence.'], 'QA = Answer + Evidence + Risk'],
      ['Exercise', ['Arrange: LLM answer, PDF upload, retrieval, chunking, embeddings.', 'Correct order: PDF upload → chunking → embeddings → retrieval → LLM answer.'], 'Put the pipeline in order']
    ]
  },
  {
    file: 'module_02_rag_architecture.pptx', title: 'Module 02 — RAG Architecture', subtitle: 'Understand the parts inside DocPilotAI',
    slides: [
      ['Big picture', ['A RAG chatbot is a pipeline, not one component.', 'Failures can happen during loading, chunking, retrieval, prompting, or generation.'], 'Loader → Chunker → Embedder → Retriever → Prompt → LLM'],
      ['Document loader', ['Reads the uploaded PDF.', 'Extracts text from pages.', 'Scanned/image-only PDFs may fail without OCR.'], 'PDF pages → extracted text'],
      ['Chunker', ['Breaks long text into smaller pieces.', 'Good chunks preserve meaningful context.', 'Bad chunks can split a rule from its condition.'], 'Long text → Chunk 1 / Chunk 2 / Chunk 3'],
      ['Embeddings + vector search', ['Embeddings represent meaning numerically.', 'The query is compared with chunk embeddings.', 'Most similar chunks are returned.'], 'Question → Similarity → Top-K chunks'],
      ['Prompt + LLM', ['Prompt gives instructions.', 'Retrieved chunks provide evidence.', 'LLM should answer only from that evidence.'], 'Instructions + Evidence + Question → Answer'],
      ['Exercise', ['Wrong answer + unrelated evidence: what likely failed first?', 'Answer: retrieval likely failed first; grounding/prompt behavior should also be checked.'], 'Find the failing component']
    ]
  },
  {
    file: 'module_03_chunking.pptx', title: 'Module 03 — Chunking', subtitle: 'How documents are split for retrieval',
    slides: [
      ['What is a chunk?', ['A chunk is a smaller piece of document text.', 'RAG searches chunks instead of the whole PDF.', 'Good chunks contain enough meaning to answer questions.'], 'Document → meaningful pieces'],
      ['Chunk size', ['Too small can lose context.', 'Too large can add noise.', 'The right size depends on document type and questions.'], 'Small / Medium / Large'],
      ['Overlap', ['Overlap repeats some text between neighboring chunks.', 'It helps when key information is near a boundary.', 'Too much overlap can create duplicates.'], 'Chunk 1 ⇄ Chunk 2'],
      ['QA risk example', ['Policy: return within 30 days if unopened.', 'If “30 days” and “if unopened” are split apart, the answer may be incomplete.'], 'Missing condition = defect'],
      ['How QA tests it', ['Ask condition-based questions.', 'Inspect retrieved evidence.', 'Check whether all required clauses are present.', 'Report incomplete answers.'], 'Question → Evidence complete?'],
      ['Exercise', ['Why should “30 days” and “if unopened” stay close together?', 'Answer: the condition changes the meaning of the return rule.'], 'Build better chunks']
    ]
  },
  {
    file: 'module_04_embeddings.pptx', title: 'Module 04 — Embeddings', subtitle: 'Meaning converted into searchable numbers',
    slides: [
      ['Simple definition', ['An embedding is a numeric representation of meaning.', 'Similar text gets similar patterns.', 'QA does not need the math to test behavior.'], 'Meaning → numbers'],
      ['Semantic similarity', ['“Password reset” can match “recover account access”.', 'Embeddings search meaning, not just exact keywords.'], 'Similar meaning = close'],
      ['Why QA cares', ['Different wording may retrieve different evidence.', 'Synonyms may work or fail.', 'Natural-language questions can expose retrieval inconsistency.'], 'Same intent, different wording'],
      ['Testing embeddings', ['Ask the same intent in multiple phrasings.', 'Use synonyms and paraphrases.', 'Compare retrieved evidence for consistency.'], '3 questions → same evidence?'],
      ['Example', ['Question: “How can I recover my account?”', 'Good match: Password reset instructions.', 'Bad match: Account deletion policy.'], 'Choose closest meaning'],
      ['Exercise', ['Closest to “How long is the reset link valid?”', 'A) Link expires after 30 minutes', 'B) Change profile photo', 'C) Support hours', 'Answer: A'], 'Similarity practice']
    ]
  },
  {
    file: 'module_05_vector_search_retrieval.pptx', title: 'Module 05 — Vector Search & Retrieval', subtitle: 'How the right evidence is selected',
    slides: [
      ['Retrieval in one sentence', ['The question is compared with document chunks.', 'The most similar chunks are returned.', 'The LLM answers from those chunks.'], 'Question → Search → Top-K'],
      ['Top-K', ['Top-K is how many chunks are returned.', 'Too few may miss context.', 'Too many may add irrelevant noise.'], 'Top 1 / Top 3 / Top 5'],
      ['Retrieval failure', ['The correct answer may exist in the PDF but not be retrieved.', 'The model may say it does not know or use unrelated evidence.'], 'Answer exists ≠ retrieved'],
      ['QA checks', ['Does evidence contain the answer?', 'Is evidence relevant?', 'Are important conditions included?', 'Does answer match evidence?'], 'Evidence quality checklist'],
      ['Example bug', ['Question: Can opened cartons be returned?', 'Evidence shows “30 days” but not “unopened”.', 'Answer says yes within 30 days.', 'Defect: missing condition.'], 'Incomplete retrieval → misleading answer'],
      ['Exercise', ['When an answer seems wrong, what should QA check first?', 'Answer: inspect whether retrieved evidence is relevant and contains the needed information.'], 'Start with evidence']
    ]
  },
  {
    file: 'module_06_grounding_hallucination.pptx', title: 'Module 06 — Grounding & Hallucination', subtitle: 'Testing whether the answer is supported',
    slides: [
      ['Grounded answer', ['A grounded answer is supported by retrieved evidence.', 'The evidence should say the same thing as the answer.'], 'Answer ↔ Evidence'],
      ['Hallucination', ['A hallucination is unsupported or invented information.', 'It may sound confident but not exist in the PDF.'], 'Confident ≠ correct'],
      ['Partial grounding', ['Some details may be supported and others invented.', 'These mixed answers are common RAG defects.'], 'Supported + Unsupported'],
      ['Out-of-scope handling', ['If evidence does not contain the answer, the agent should say it does not know.', 'A helpful invented answer is still a defect.'], 'No evidence → I do not know'],
      ['Bug report fields', ['Question', 'Expected behavior', 'Actual answer', 'Evidence shown', 'Why unsupported', 'Severity/impact'], 'AI QA defect template'],
      ['Exercise', ['Answer: “Refunds take 10 business days.”', 'Evidence only says returns are accepted within 30 days.', 'Classification: Hallucinated / unsupported.'], 'Classify answer quality']
    ]
  },
  {
    file: 'module_07_rag_testing_final_project.pptx', title: 'Module 07 — RAG Testing + Final Project', subtitle: 'Use DocPilotAI as a real AI QA lab',
    slides: [
      ['What QA tests', ['Answer correctness', 'Retrieval relevance', 'Grounding / faithfulness', 'Missing conditions', 'Out-of-scope behavior', 'Prompt robustness'], 'RAG QA test types'],
      ['Good test case', ['Scenario', 'Question/input', 'Expected answer', 'Expected evidence', 'Actual answer', 'PASS/FAIL', 'Notes'], 'AI QA test template'],
      ['Positive + negative coverage', ['Happy path factual question', 'Unsupported question', 'Condition-based question', 'Paraphrased query', 'Ambiguous/edge prompt'], 'Balanced test coverage'],
      ['Bug reporting', ['Link failed test.', 'Capture exact answer.', 'Capture evidence.', 'Explain why behavior is wrong.', 'Set severity based on impact.'], 'Failure → defect'],
      ['Final project', ['Upload a PDF.', 'Ask multiple questions.', 'Create 15 test cases.', 'Log 3 defects.', 'Review QA score.', 'Download final report.'], 'DocPilotAI hands-on project'],
      ['Completion', ['Student can explain RAG.', 'Student can inspect evidence.', 'Student can design AI QA tests.', 'Student can report hallucination/retrieval defects.'], 'Learn → Test → Diagnose → Report']
    ]
  }
];

function addDeck(module) {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.author = 'DocPilotAI';
  pptx.subject = 'RAG for QA Students';
  pptx.title = module.title;
  pptx.theme = { headFontFace: 'Aptos Display', bodyFontFace: 'Aptos', lang: 'en-US' };

  module.slides.forEach((s, i) => {
    const slide = pptx.addSlide();
    slide.background = { color: '0B1020' };
    slide.addText(i === 0 ? module.title : s[0], { x: 0.65, y: 0.45, w: 8.5, h: 0.55, fontSize: 27, bold: true, color: 'FFFFFF', margin: 0 });
    slide.addText(i === 0 ? module.subtitle : module.title, { x: 0.68, y: 1.02, w: 8.5, h: 0.28, fontSize: 11.5, color: '93C5FD', margin: 0 });
    slide.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 1.6, w: 6.0, h: 4.65, rectRadius: 0.12, fill: { color: '111827' }, line: { color: '334155', width: 1 } });
    slide.addText('Key teaching points', { x: 1.0, y: 1.9, w: 4.8, h: 0.3, fontSize: 13, bold: true, color: '67E8F9', margin: 0 });
    slide.addText(s[1].map(x => '• ' + x).join('\n'), { x: 1.0, y: 2.35, w: 5.35, h: 3.25, fontSize: 18, color: 'F8FAFC', breakLine: false, valign: 'top', margin: 0.05, paraSpaceAfterPt: 10, fit: 'shrink' });
    slide.addShape(pptx.ShapeType.roundRect, { x: 7.15, y: 1.6, w: 5.45, h: 4.65, rectRadius: 0.12, fill: { color: '172554' }, line: { color: '3B82F6', transparency: 25, width: 1.2 } });
    slide.addText('VISUAL', { x: 7.55, y: 2.0, w: 1.5, h: 0.28, fontSize: 11, bold: true, color: 'A5B4FC', margin: 0 });
    slide.addText(s[2], { x: 7.55, y: 2.65, w: 4.65, h: 1.75, fontSize: 24, bold: true, color: 'FFFFFF', align: 'center', valign: 'mid', margin: 0.05, fit: 'shrink' });
    slide.addText('QA connection', { x: 7.55, y: 4.8, w: 2.0, h: 0.28, fontSize: 11, bold: true, color: '67E8F9', margin: 0 });
    slide.addText('Ask: what can fail here, and how would we prove it?', { x: 7.55, y: 5.15, w: 4.45, h: 0.65, fontSize: 13.5, color: 'DBEAFE', margin: 0 });
    slide.addText(`DocPilotAI · ${String(i + 1).padStart(2, '0')}`, { x: 10.7, y: 7.05, w: 1.8, h: 0.2, fontSize: 8.5, color: '64748B', align: 'right', margin: 0 });
  });
  return pptx.writeFile({ fileName: path.join(outDir, module.file) });
}

(async () => {
  for (const module of modules) await addDeck(module);
  console.log(`Generated ${modules.length} RAG learning decks in ${outDir}`);
})();
