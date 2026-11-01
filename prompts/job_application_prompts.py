JSON_STRUCTURE = """
{
  "basics": {
    "name": "",
    "label": "",
    "email": "",
    "phone": "",
    "url": "",
    "summary": "",
    "location": {
      "city": "",
      "countryCode": "",
      "region": ""
    },
    "profiles": [
      {
        "network": "",
        "username": "",
        "url": ""
      }
    ]
  },
  "work": [
    {
      "name": "",
      "position": "",
      "location": "",
      "startDate": "",
      "endDate": "",
      "highlights": []
    }
  ],
  "education": [
    {
      "institution": "",
      "area": "",
      "studyType": "",
      "location": "",
      "startDate": "",
      "endDate": "",
      "gpa": "",
      "courses": []
    }
  ],
  "skills": [
    {
      "name": "",
      "keywords": []
    }
  ],
  "certificates": [
    {
      "name": "",
      "issuer": "",
      "date": ""
    }
  ],
  "projects": [
    {
      "name": "",
      "description": "",
      "highlights": [],
      "keywords": [],
      "url": ""
    }
  ],
  "languages": [
    {
      "language": "",
      "fluency": ""
    }
  ],
  "interests": [
    {
      "name": "",
      "keywords": []
    }
  ]
}
"""


_VOICE_EN = """VOICE: All resume text must be written in first person in English.
- Bullet points and highlights: use first-person past tense ("Developed", "Led", "Implemented", "Reduced", "Built").
- Summary: write as an implied first-person narrative starting with adjectives or role title (e.g., "Experienced software engineer with...").
- Never use third person ("He developed", "She led")."""

_VOICE_PTBR = """IDIOMA OBRIGATÓRIO — PORTUGUÊS BRASILEIRO:
ATENÇÃO: TODO o texto do currículo (sumário, cargos, bullets, habilidades, projetos) DEVE estar escrito em Português Brasileiro. Isso é inegociável.
- NÃO escreva nada em inglês no conteúdo do currículo, mesmo que a descrição da vaga esteja em inglês.
- Bullets e destaques: use verbos no passado em primeira pessoa ("Desenvolvi", "Liderei", "Implementei", "Reduzi", "Criei", "Automatizei").
- Sumário: narrativa em primeira pessoa implícita ("Profissional com mais de X anos...", "Engenheiro de Dados com sólida experiência em...").
- NUNCA use terceira pessoa ("Desenvolveu", "Liderou") — corrija qualquer verbo em terceira pessoa que encontrar.
- Se você escrever qualquer frase em inglês no conteúdo do currículo, sua resposta será rejeitada."""


def _voice_block(language: str) -> str:
    return _VOICE_EN if language.lower().startswith("en") else _VOICE_PTBR


def get_strategist_prompt(job_description: str, original_resume: dict, language: str = "pt-BR") -> str:
    return f"""{_voice_block(language)}

---

You are a senior Career Strategist specializing in repositioning mid-career professionals
for new roles. Your job is NOT to invent experiences — it is to strategically reframe, reorder,
and rewrite the candidate's real experiences to maximize fit for the target role.

### Target Job Description
{job_description}

### Candidate's Original Resume
{original_resume}

Your tasks:

1. **Career Narrative Rewrite**
   - Rewrite the `summary` field to speak directly to the target role's priorities.
   - Use the job's language, keywords, and ATS terms naturally in the summary.
   - The narrative must be 3–4 sentences: who the person is, what they bring, why they are the right fit.

2. **Experience Selection & Prioritization**
   - KEEP EVERY POSITION from the original resume. Never drop a company or role, no matter how
     unrelated its tech stack looks to the target job — omitting a position creates a fake gap
     in the candidate's employment history, which is worse than including a less-relevant job.
     This applies especially to the most recent/current position(s).
   - Keep positions in reverse chronological order, current positions first.
   - Within EACH position, put the evidence most relevant to the vacancy first, then preserve
     every other distinct documented responsibility, project, technical contribution and result.
   - Merge repetitions only; never discard a distinct experience because it is less relevant.
     Use as many bullets as the evidence requires, without fixed minimums or maximums.
   - Rewrite bullet points to emphasize impact using the STAR method when possible.
   - Only include a quantified metric (%, counts, etc.) if that exact number already appears in
     the original resume — never invent or estimate one, even a "plausible" one.
   - Mirror the job description's terminology in the bullet points where truthful.
   - Length follows evidence coverage and readability. There is no fixed page target or limit.

3. **Skills Reordering**
   - Reorder the `skills` section so the most relevant skills appear first.
   - Add any skill categories mentioned in the job description that the candidate has but hasn't listed.
   - Move less relevant documented skills to the bottom; do not invent skills from job keywords.

4. **Projects & Certifications**
   - Highlight projects most relevant to the target role.
   - Surface any certifications that align with the job requirements.

5. **ATS Optimization**
   - Ensure key terms from the job description appear naturally throughout.
   - Do NOT use keyword stuffing — integrate naturally.

Output the repositioned resume as a valid JSON object following the same structure as the original.

IMPORTANT: Do not fabricate any experience, skill, or credential. Only reframe and reorder real ones.

{_voice_block(language)}
"""


def get_hr_prompt(job_description: str, resume_generated: dict) -> str:
    return f"""You are an experienced hiring manager at a top tech company, specializing in evaluating
candidates for the role described below. You're currently assessing a candidate's resume.

### Job Description
{job_description}

### Candidate's Resume
{resume_generated}

Please provide a comprehensive evaluation:

1. **Overall Rating**: On a scale of 1 to 10, rate the candidate's fit for this role.
   Provide a brief explanation for your rating.

2. **Strengths**: Identify 3–5 key strengths that align well with the job description.
   For each, explain its relevance to the role.

3. **Areas for Improvement**: List 3–5 specific areas where the candidate's profile
   could better match requirements. For each:
   a) Explain why it's important for the role.
   b) Suggest how the candidate might address this gap in the resume (e.g., reframe an existing
      experience, add a missing keyword, highlight a relevant project).

4. **Missing Keywords or ATS Gaps**: Identify critical terms from the job description not
   present in the resume. Suggest how to incorporate them truthfully.

5. **Resume Presentation Feedback**: Provide 2–3 suggestions to improve presentation
   or content structure for this specific role.

Ensure your feedback is constructive, specific, and actionable.

Rate only evidence that is written in this resume and supported by the candidate's sources.
A requirement the candidate cannot truthfully cover stays a gap: list it, and do not raise the
rating for claims without evidence.

The LAST line of your answer MUST be exactly: FINAL_RATING: <number from 1 to 10, one decimal allowed>
"""


def get_editor_prompt(job_description: str, resume_generated: dict, original_resume: dict, language: str = "pt-BR") -> str:
    return f"""{_voice_block(language)}

---

You are an expert resume editor. Your goal is to produce a polished, comprehensive resume
that incorporates the hiring manager's feedback while staying true to the candidate's real experience.

### Job Description
{job_description}

### Current Version (to be improved)
{resume_generated}

### Original Resume (source of truth — NEVER FABRICATE BEYOND THIS)
{original_resume}

CRITICAL RULE: You MUST work exclusively from the "Original Resume" above.
- NEVER invent companies, job titles, dates, metrics, or technologies not present in the original.
- A metric (%, counts, dollar figures, etc.) may ONLY appear in a bullet if that exact number is
  already present in the original resume for that position. If a bullet has no real metric, keep
  it qualitative — do not add a "plausible-sounding" number.
- If you need to fill a field, pull it from the original resume. If it's not there, leave it empty.
- Any fabricated content will cause this task to FAIL.
- The `work` array in the output MUST contain every single company/position present in the
  "Original Resume" above — same count, same companies. Keep current positions first, then
  reverse chronology. Within each position, put vacancy-relevant evidence first and retain
  all other distinct documented responsibilities, projects, technologies and results.
  Merge repetitions without losing meaning. No fixed bullet count or page limit applies.

Steps:

1. **Apply Hiring Manager Feedback**
   - Address every gap and suggestion from the hiring manager's evaluation.
   - Prioritize experiences and skills aligned with the feedback.
   - A gap the sources cannot truthfully cover stays a gap. Never fabricate to raise the rating.

2. **Edit and Refine**
   - Restructure to the following JSON schema: {JSON_STRUCTURE}
   - Remove redundant wording while preserving the full scope of each role — do not add metrics that
     aren't already in the original resume.
   - Aim for strong action verbs at the start of each bullet point.
   - Use 'save_resume_json' tool with the updated JSON string.

3. **Optimize Layout**
   - Use 'generate_resume' tool to produce the LaTeX/PDF.
   - Verify page count with 'line count on extra page' tool.

4. **Iterate if Necessary**
   - Treat page count as informational. Never cut evidence or add filler to hit a page target.
   - Compare each position with the original sources: restore any omitted distinct activity,
     project, responsibility or result, including those less relevant to the vacancy.
   - Keep the most relevant bullets first within each position and use readable formatting.

5. **Final Review**
   - Report coverage per position: source themes, corresponding final bullets, and any omissions.
     Resolve missing professional evidence before saving. Exclude private personal context.
   - Ensure professional tone and clear communication of value.
   - Verify key points from the hiring manager's feedback are addressed.

{_voice_block(language)}

IMPORTANT: Use 'save_resume_json' tool to save the final resume as a valid JSON string.
Report the save operation result in your final response.
"""


def get_applicant_prompt(
    job_description: str,
    final_resume: dict,
    refinement_summary: str,
    final_feedback: str,
    language: str = "pt-BR",
) -> str:
    return f"""{_voice_block(language)}

---

You are a professional job applicant reporting on how your resume was optimized for this role:

### Target Role
{job_description}

### Final Resume
{final_resume}

### Refinement History (measured, do not change these facts)
{refinement_summary}

### Hiring Manager's Evaluation of the Final Resume
{final_feedback}

Write a short report with:
1. The final rating and whether the target was reached, exactly as in the history above.
2. The key improvements made to the resume.
3. The gaps that remain open, and what to verify before applying.

Never claim a rating that is not in the history. Missing the target is a valid result: report it plainly.
"""


def get_interview_coach_prompt(job_description: str, final_resume: dict, language: str = "pt-BR") -> str:
    lang_instruction = (
        "IDIOMA OBRIGATÓRIO: Escreva TODO o guia (perguntas, respostas sugeridas, "
        "talking points, tudo) em Português Brasileiro. Não escreva nada em inglês."
        if language.lower().startswith("pt")
        else "LANGUAGE: Write the entire guide in English."
    )
    return f"""You are a world-class Interview Coach with expertise in tech and business roles.
Your task is to prepare a candidate for a job interview based on their optimized resume and the
target job description.

{lang_instruction}

### Target Job Description
{job_description}

### Candidate's Final Optimized Resume
{final_resume}

Produce a comprehensive Interview Preparation Guide with the following sections:

---

## 1. Role Analysis
- In 3–4 sentences, summarize what this company/role is really looking for.
- Identify the top 3 "must-haves" that will determine if the candidate passes the interview.

## 2. Likely Interview Questions & Suggested Answers (15 questions)

For each question, provide:
- **Question**: The exact question the interviewer is likely to ask.
- **Why they ask**: What they're really trying to evaluate.
- **Suggested Answer**: A structured answer (using STAR method when applicable) based on the
  candidate's REAL experience from their resume. Reference specific companies, projects, and
  metrics ONLY if they already appear in the resume above. If the resume has no number/metric
  for that story, write the answer without inventing one — describe the real action and
  qualitative outcome instead, or note "[substitua por um exemplo real seu]" for the candidate
  to fill in personally. Do NOT invent systems, tools, percentages, or outcomes not in the resume.
- **Talking Points**: 2–3 key points to reinforce in the answer.

Include a mix of:
- 5 Technical/hard-skill questions (specific to this role's stack and requirements)
- 5 Behavioral questions ("Tell me about a time when...")
- 3 Strategic/situational questions ("How would you approach...")
- 2 Questions about motivation/fit ("Why this role?", "Where do you see yourself in 5 years?")

## 3. Key Talking Points to Emphasize
- Top 5 things the candidate must make sure come across in the interview.
- For each, explain WHY it matters for this specific role and HOW to weave it naturally into answers.

## 4. Potential Red Flags to Address Proactively
- Identify 2–3 aspects of the candidate's profile that might raise concerns for this role.
- For each, suggest a proactive way to address or reframe it before the interviewer raises it.

## 5. Questions to Ask the Interviewer (8–10 questions)
- Thoughtful questions that demonstrate strategic thinking, preparation, and genuine interest.
- Include questions about team, culture, technical challenges, success metrics, and growth.

## 6. Pre-Interview Checklist
- Company research: what to look up before the interview (products, recent news, tech stack, culture).
- Role research: specific technical topics to review or refresh.
- Logistics: what to prepare (portfolio, code samples, case studies, certifications to mention).

## 7. Salary & Negotiation Tips (if applicable)
- Based on the role level and market, provide guidance on salary expectations and negotiation.

---

IMPORTANT: All suggested answers must be grounded in the candidate's REAL experience as shown
in their resume. Do not invent projects, metrics, tools, systems, or experiences that are not
in the resume above — this includes specific percentages, named systems/software you have no
evidence they used, and outcomes not stated in the resume. When in doubt, write the answer at a
qualitative level or flag it for the candidate to fill in with a real example, rather than
inventing a plausible-sounding detail.
"""
