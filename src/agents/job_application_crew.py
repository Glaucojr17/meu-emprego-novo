import json
import logging
import os
import sys
from pathlib import Path
from textwrap import dedent

from crewai import Agent, Crew, Process, Task

current_dir = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir)

from prompts.job_application_prompts import (
    get_applicant_prompt,
    get_editor_prompt,
    get_hr_prompt,
    get_interview_coach_prompt,
    get_strategist_prompt,
)
from resume.generator import generate
from src.agents.refinement import DEFAULT_MAX_REVISIONS, TARGET_RATING, refine
from tools.resume_tools import (
    generate_resume_tool,
    pgcount_tool,
    save_interview_prep_tool,
    save_resume_json,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class JobApplicationCrew:
    def __init__(
        self,
        role: str = None,
        job_profile_path: str = "data/dev_procurando/job_desc.txt",
        output_dir: str = "outputs",
        provider: str = None,
        language: str = "pt-BR",
        original_resume_path: str = "data/dev_procurando/resume.json",
    ):
        self.role = role
        self.job_profile_path = job_profile_path
        self.output_dir = output_dir
        self.provider = provider
        self.language = language
        self.original_resume_path = original_resume_path

        os.environ["RESUME_OUTPUT_DIR"] = output_dir

        with open(job_profile_path, "r", encoding="utf-8") as f:
            self.job_description = f.read()

        with open(original_resume_path, "r", encoding="utf-8") as f:
            self.original_resume = json.load(f)

        # Load only this person's supporting sources. Keep the canonical JSON untouched.
        person = Path(original_resume_path).parent.name
        self.source_context = ""
        for filename in ("profile_truth.md", "about_me.md"):
            source = Path("input") / person / filename
            if source.exists():
                self.source_context += f"\n### {filename}\n{source.read_text(encoding='utf-8')}\n"
        self.source_context = (
            "\nSOURCE RULES: profile_truth.md corrections and exclusions override the base JSON "
            "and about_me.md. Use about_me.md only for complementary professional evidence. "
            "Ignore placeholders and unconfirmed credentials. Preserve expired certification "
            "status and education in progress. ALWAYS include every academic degree from profile_truth.md in the education section; never omit or shorten the education list. Never include family health or private personal "
            "context in the resume. Do not attribute general skills to specific employers without "
            "evidence. These documents supplement the Original Resume as factual sources.\n"
            + self.source_context
        )
        os.environ["RESUME_LANGUAGE"] = language

        generated_resume_path = os.path.join(output_dir, "json", "resume.json")
        if os.path.exists(generated_resume_path):
            with open(generated_resume_path, "r", encoding="utf-8") as f:
                self.resume_generated = json.load(f)
        else:
            self.resume_generated = self.original_resume

        self.llm = self._get_llm()

    def _get_llm(self):
        from src.llm_factory import get_llm
        return get_llm(provider=self.provider)

    @property
    def _resume_path(self) -> Path:
        return Path(self.output_dir, "json", "resume.json")

    def _current_resume(self) -> dict:
        return json.loads(self._resume_path.read_text(encoding="utf-8"))

    def _kickoff(self, agents, tasks):
        crew = Crew(agents=agents, tasks=tasks, verbose=True, process=Process.sequential)
        result = crew.kickoff()
        logger.info(crew.usage_metrics)
        logger.info(f"Token Usage: {result.token_usage}")
        return result

    def _snapshot(self):
        return self._resume_path.read_bytes(), self.coverage_audit

    def _restore(self, state):
        resume_bytes, self.coverage_audit = state
        self._resume_path.write_bytes(resume_bytes)

    def _render(self):
        generate(
            json_path=str(self._resume_path),
            latex_path=os.path.join(self.output_dir, "latex", "output_resume.tex"),
            pdf_dir=os.path.join(self.output_dir, "pdf"),
        )

    def _evaluate(self, hiring_manager) -> str:
        task = Task(
            description=dedent(get_hr_prompt(self.job_description, self._current_resume()) + self.source_context
                + "\nDo not recommend cuts for page count."),
            agent=hiring_manager,
            expected_output="An evaluation report ending with the line 'FINAL_RATING: <number>'.",
        )
        self._kickoff([hiring_manager], [task])
        return task.output.raw

    def _revise(self, resume_editor, feedback: str) -> None:
        task = Task(
            description=dedent(
                get_editor_prompt(
                    self.job_description, self._current_resume(), self.original_resume, self.language
                ) + self.source_context + f"\n### Hiring Manager's Latest Evaluation\n{feedback}\n"
            ),
            agent=resume_editor,
            expected_output=(
                "A comprehensive resume saved as JSON and PDF, addressing the hiring manager's "
                "feedback, with a per-position coverage audit and confirmation of the save."
            ),
        )
        self._kickoff([resume_editor], [task])
        self.coverage_audit = task.output.raw

    def run(self):
        llm_kwargs = {"llm": self.llm} if self.llm else {}

        career_strategist = Agent(
            name="Career Strategist",
            role="Senior Career Strategist specializing in professional repositioning",
            goal=(
                "Rewrite the candidate's resume narrative and strategically reframe their "
                "experiences to maximize fit for the target job, without fabricating anything."
            ),
            backstory=(
                "You have helped hundreds of mid-career professionals pivot into new roles by "
                "surfacing the hidden relevance of their existing experience. You know that "
                "the same career can tell many different stories — your job is to tell the "
                "right story for this specific role."
            ),
            verbose=True,
            allow_delegation=False,
            **llm_kwargs,
        )

        hiring_manager = Agent(
            name="Hiring Manager",
            role="Experienced hiring manager specializing in tech roles",
            goal="Evaluate candidate resumes and provide constructive, actionable feedback",
            backstory=(
                "You have years of experience hiring for top tech companies and know exactly "
                "what makes a strong candidate. You provide detailed feedback and accurate "
                "ratings based on job requirements."
            ),
            verbose=True,
            allow_delegation=False,
            **llm_kwargs,
        )

        resume_editor = Agent(
            name="Resume Editor",
            role="Expert resume editor with tech industry knowledge",
            goal="Preserve every position's full documented scope, with vacancy-relevant evidence first",
            backstory=(
                "You've helped countless tech professionals land their dream jobs by crafting "
                "complete, readable resumes with length determined by evidence coverage."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[generate_resume_tool, pgcount_tool, save_resume_json],
            **llm_kwargs,
        )

        job_applicant = Agent(
            name="Job Applicant",
            role="Motivated professional seeking to optimize their job application",
            goal="Report honestly how the resume was optimized and what remains open before applying",
            backstory=(
                "You want the best application you can truthfully send. You know a rating below "
                "target can reflect a real gap, and you would rather know it than hide it."
            ),
            verbose=True,
            allow_delegation=False,
            **llm_kwargs,
        )

        interview_coach = Agent(
            name="Interview Coach",
            role="World-class Interview Coach for tech and business professionals",
            goal=(
                "Produce a comprehensive interview preparation guide tailored to the candidate's "
                "real experience and the specific job requirements."
            ),
            backstory=(
                "You have coached hundreds of candidates for interviews at top companies. "
                "You know what interviewers look for and how to help candidates tell compelling, "
                "authentic stories from their actual experience."
            ),
            verbose=True,
            allow_delegation=False,
            **llm_kwargs,
        )

        reposition_resume = Task(
            description=dedent(get_strategist_prompt(self.job_description, self.original_resume, self.language) + self.source_context),
            agent=career_strategist,
            expected_output=(
                "A repositioned resume as a valid JSON object with the same structure as the input, "
                "with the summary rewritten, experiences prioritized and reframed, and skills "
                "reordered for the target role. No fabricated information."
            ),
        )

        evaluate_resume = Task(
            description=dedent(get_hr_prompt(self.job_description, self.original_resume) + self.source_context
                + "\nEvaluate the strategist's NEW JSON in task context, not an older draft. Audit coverage per position against all sources; do not recommend cuts for page count."),
            agent=hiring_manager,
            expected_output=(
                "A comprehensive evaluation report including: numerical rating (1–10), "
                "strengths, areas for improvement, missing ATS keywords, and resume "
                "presentation feedback."
            ),
            context=[reposition_resume],
        )

        edit_resume = Task(
            description=dedent(
                get_editor_prompt(
                    self.job_description, self.original_resume, self.original_resume, self.language
                ) + self.source_context + "\nUse the strategist's NEW JSON from task context as the current draft."
            ),
            agent=resume_editor,
            expected_output=(
                "A comprehensive resume saved as JSON and PDF, addressing the hiring "
                "manager's feedback with coverage of every position. Includes a per-position coverage audit and confirmation that "
                "the file was saved."
            ),
            context=[reposition_resume, evaluate_resume],
        )

        self._kickoff(
            [career_strategist, hiring_manager, resume_editor],
            [reposition_resume, evaluate_resume, edit_resume],
        )
        self.coverage_audit = getattr(getattr(edit_resume, "output", None), "raw", None)

        refinement = refine(
            evaluate=lambda: self._evaluate(hiring_manager),
            revise=lambda feedback: self._revise(resume_editor, feedback),
            snapshot=self._snapshot,
            restore=self._restore,
            target=TARGET_RATING,
            max_revisions=int(os.getenv("RESUME_MAX_REVISIONS") or DEFAULT_MAX_REVISIONS),
        )
        logger.info(f"Refinement finished:\n{refinement.summary()}")

        # The PDF must always match the final JSON, whatever the last agent did.
        self._render()
        final_resume = self._current_resume()

        optimize_application = Task(
            description=dedent(
                get_applicant_prompt(
                    self.job_description,
                    final_resume,
                    refinement.summary(),
                    refinement.final_feedback,
                    self.language,
                ) + self.source_context
            ),
            agent=job_applicant,
            expected_output=(
                "A report with: final rating and whether the target was reached, key "
                "improvements made, and the gaps that remain open."
            ),
        )

        prepare_interview = Task(
            description=dedent(
                get_interview_coach_prompt(self.job_description, final_resume, self.language) + self.source_context
            ),
            agent=interview_coach,
            expected_output=(
                "A comprehensive interview preparation guide saved as 'interview_prep.md' in "
                "the output directory, including: role analysis, 15 likely questions with "
                "suggested answers, key talking points, red flags to address, questions to ask "
                "the interviewer, pre-interview checklist, and salary/negotiation tips."
            ),
            context=[optimize_application],
        )

        result = self._kickoff(
            [job_applicant, interview_coach],
            [optimize_application, prepare_interview],
        )

        interview_content = getattr(getattr(prepare_interview, "output", None), "raw", None)
        if interview_content:
            interview_path = os.path.join(self.output_dir, "interview_prep.md")
            with open(interview_path, "w", encoding="utf-8") as f:
                f.write(interview_content)
            logger.info(f"Interview prep saved to: {interview_path}")

        if self.coverage_audit:
            Path(self.output_dir, "coverage_review.md").write_text(self.coverage_audit, encoding="utf-8")

        report = getattr(getattr(optimize_application, "output", None), "raw", None)
        if report:
            Path(self.output_dir, "rating_report.md").write_text(
                f"{refinement.summary()}\n\n{report}\n", encoding="utf-8"
            )

        role_label = f" [{self.role}]" if self.role else ""
        logger.info(f"Outputs{role_label} saved to: {self.output_dir}/")

        return result


def main():
    job_application_crew = JobApplicationCrew()
    final_result = job_application_crew.run()
    logger.info(final_result)
