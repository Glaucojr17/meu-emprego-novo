import json
import os
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.platform_app import core, sources
from src.platform_app.web import app, token


POLICY = {"titles": ["DevOps"], "skills": ["Kubernetes", "Terraform"],
          "exclude": ["presencial"], "remote_only": True}


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.patcher = patch.object(core, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_collect_dedup_and_preserve_status(self):
        output = self.root / "outputs" / "glaucojunior" / "platform"
        con = core.database(output)
        item = sources.job("Remotive", "https://remotive.com/remote-jobs/devops?id=1",
                           "DevOps Engineer", "Exemplo", "Remoto — Worldwide",
                           "Kubernetes e Terraform")
        self.assertEqual(core.import_jobs(con, [item, item], POLICY), 1)
        row = con.execute("SELECT * FROM jobs").fetchone()
        self.assertEqual(row["eligible"], 1)
        con.execute("UPDATE jobs SET status='avaliar' WHERE id=?", (row["id"],))
        con.commit()
        self.assertEqual(core.import_jobs(con, [item], POLICY), 0)
        self.assertEqual(con.execute("SELECT status FROM jobs").fetchone()[0], "avaliar")
        con.close()

    def test_restrict_country_and_preserve_all_original_experience(self):
        self.assertFalse(core.geography_ok("Remoto — US only"))
        self.assertTrue(core.geography_ok("Remoto — LATAM"))
        base = json.loads((Path(__file__).resolve().parents[1] /
                           "examples/dev_procurando/resume.json").read_text())
        row = {"title": "DevOps Engineer", "description": "Terraform and Kubernetes"}
        result, _ = core.adapt_resume(base, row, POLICY)
        self.assertEqual([x["name"] for x in result["work"]],
                         [x["name"] for x in base["work"]])
        for original, adapted in zip(base["work"], result["work"]):
            self.assertCountEqual(original["highlights"], adapted["highlights"])
        self.assertEqual(result["basics"], base["basics"])

    def test_generate_pdf_and_interview_without_paid_api(self):
        private = self.root / "data" / "glaucojunior"
        private.mkdir(parents=True)
        source = Path(__file__).resolve().parents[1] / "examples/dev_procurando/resume.json"
        (private / "resume.json").write_bytes(source.read_bytes())
        output = self.root / "outputs" / "glaucojunior" / "platform"
        con = core.database(output)
        job = sources.job("Remotive", "https://remotive.com/remote-jobs/devops",
                          "DevOps Engineer", "Exemplo", "Remoto — Worldwide", "Terraform")
        core.import_jobs(con, [job], POLICY)
        row = con.execute("SELECT * FROM jobs").fetchone()
        core.generate(con, row, "glaucojunior", POLICY, output)
        dest = output / "documents" / row["id"]
        self.assertTrue((dest / "resume.pdf").read_bytes().startswith(b"%PDF"))
        self.assertIn("Launchpad Labs", (dest / "interview.md").read_text())
        self.assertIsNotNone(con.execute("SELECT generated_at FROM jobs").fetchone()[0])
        con.close()

    def test_run_from_private_csv_creates_documents_and_keeps_manual_status(self):
        private = self.root / "input" / "glaucojunior"
        private.mkdir(parents=True)
        (private / "platform.json").write_text(json.dumps({
            "person": "glaucojunior", "remotive": False, "arbeitnow": False,
            "greenhouse_boards": [], "lever_sites": [], "himalayas_queries": [],
            "devops_brasil": False, "require_portuguese": False,
            "require_known_date": False,
            "gmail_query": "",
            "max_new_documents_per_run": 2}))
        (private / "job_policy.json").write_text(json.dumps(POLICY))
        (private / "vagas.csv").write_text(
            "source,url,title,company,location,description\n"
            "manual,https://empresa.gupy.io/jobs/123,DevOps Engineer,Empresa,Remoto Brasil,Terraform\n")
        master = self.root / "data" / "glaucojunior"
        master.mkdir(parents=True)
        example = Path(__file__).resolve().parents[1] / "examples/dev_procurando/resume.json"
        (master / "resume.json").write_bytes(example.read_bytes())
        result = core.run("glaucojunior")
        self.assertEqual((result["new"], result["generated"], result["errors"]), (1, 1, []))
        output = self.root / "outputs" / "glaucojunior" / "platform"
        con = core.database(output)
        identity = con.execute("SELECT id FROM jobs").fetchone()[0]
        con.execute("UPDATE jobs SET status='avaliar' WHERE id=?", (identity,))
        con.commit()
        con.close()
        second = core.run("glaucojunior")
        self.assertEqual((second["new"], second["generated"]), (0, 0))
        con = core.database(output)
        self.assertEqual(con.execute("SELECT status FROM jobs").fetchone()[0], "avaliar")
        con.close()

    def test_public_source_normalization(self):
        with patch.object(sources, "fetch_json", return_value={"jobs": [{
            "url": "https://remotive.com/remote-jobs/devops-1", "title": "DevOps",
            "company_name": "Exemplo", "candidate_required_location": "Worldwide",
            "description": "<p>Terraform &amp; Linux</p>",
            "publication_date": "2026-11-02T12:00:00"}]}):
            base = self.root / "input" / "glaucojunior"
            base.mkdir(parents=True)
            jobs = sources.remotive(base)
            self.assertEqual(jobs[0]["description"], "Terraform & Linux")
            self.assertIn("Remoto", jobs[0]["location"])
            self.assertEqual(jobs[0]["published_at"], "2026-11-02T12:00:00")
            self.assertEqual(len(sources.remotive(base)), 1)  # cache, sem nova requisição

    def test_recent_brazilian_role_only_and_legacy_db_migration(self):
        output = self.root / "outputs" / "glaucojunior" / "platform"
        output.mkdir(parents=True)
        old = sqlite3.connect(output / "jobs.sqlite3")
        old.execute("""CREATE TABLE jobs (
            id TEXT PRIMARY KEY, url TEXT NOT NULL UNIQUE, source TEXT NOT NULL,
            title TEXT NOT NULL, company TEXT NOT NULL, location TEXT NOT NULL,
            description TEXT NOT NULL, score INTEGER NOT NULL, eligible INTEGER NOT NULL,
            reasons TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'nova',
            first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, generated_at TEXT,
            generation_error TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT ''
        )""")
        old.commit()
        old.close()
        con = core.database(output)
        self.assertIn("published_at", {r[1] for r in con.execute("PRAGMA table_info(jobs)")})
        settings = {"brazil_only": True, "require_portuguese": True, "max_age_days": 30}
        today = date.today()
        jobs = [
            sources.job("Teste", f"https://example.com/{label}", title, "Empresa",
                        location, description, published_at=published)
            for label, title, location, description, published in (
                ("good", "Analista DevOps", "Remoto — Brasil",
                 "Requisitos: Kubernetes. Experiência com Terraform.",
                 today.isoformat()),
                ("old", "Analista DevOps", "Remoto — Brasil",
                 "Requisitos: Kubernetes. Experiência com Terraform.",
                 (today - timedelta(days=61)).isoformat()),
                ("english", "DevOps Engineer", "Remoto — Brasil",
                 "Requirements: Kubernetes. Experience with Terraform.",
                 today.isoformat()),
                ("country", "DevOps Engineer", "Remoto — USA only",
                 "Requisitos: Kubernetes. Experiência com Terraform.",
                 today.isoformat()),
                ("role", "Backend Developer", "Remoto — Brasil",
                 "Requisitos: Kubernetes. Experiência com Terraform.",
                 today.isoformat()),
            )
        ]
        self.assertEqual(core.import_jobs(con, jobs, POLICY, settings), 5)
        no_date = sources.job("Alerta", "https://example.com/unknown",
                              "DevOps", "Empresa", "Remoto — Brasil",
                              "Requisitos: Kubernetes. Experiência com Terraform.")
        core.import_jobs(con, [no_date], POLICY, settings)
        self.assertEqual(con.execute(
            "SELECT eligible FROM jobs WHERE url='https://example.com/unknown'").fetchone()[0], 0)
        eligible = con.execute("SELECT title FROM jobs WHERE eligible=1").fetchall()
        self.assertEqual([r[0] for r in eligible], ["Analista DevOps"])
        con.execute("UPDATE jobs SET status='avaliar' WHERE url='https://example.com/good'")
        con.commit()
        core.recheck_existing(con, POLICY, settings)
        self.assertEqual(con.execute(
            "SELECT status, published_at FROM jobs WHERE url='https://example.com/good'").fetchone()[:],
            ("avaliar", today.isoformat()))
        con.close()

    def test_himalayas_and_brazil_board_date_semantics(self):
        now = int(datetime.now(timezone.utc).timestamp())
        def fake_fetch(url, domain):
            if domain == "himalayas.app":
                self.assertIn("country=BR", url)
                return {"jobs": [{
                    "title": "DevOps Engineer", "companyName": "Exemplo",
                    "applicationLink": "https://himalayas.app/companies/exemplo/jobs/devops",
                    "description": "Requisitos e experiência em Kubernetes.",
                    "locationRestrictions": [{"alpha2": "BR"}], "pubDate": now,
                    "expiryDate": now + 86400 * 20
                }]}
            return [{
                "title": "Analista DevOps", "html_url": "https://github.com/DevOps-Brasil/Vagas/issues/1",
                "created_at": "2026-11-04T10:00:00Z",
                "body": "### 🏢 Empresa\nExemplo\n### 📋 Descrição\nRequisitos e experiência",
                "labels": [{"name": "Remoto"}]
            }]
        with patch.object(sources, "fetch_json", side_effect=fake_fetch):
            base = self.root / "input" / "glaucojunior"
            base.mkdir(parents=True)
            himalayas = sources.himalayas(base, ["DevOps"])
            board = sources.devops_brasil(base)
        self.assertIsNone(himalayas[0]["published_at"])
        self.assertEqual(core.normalize_date(himalayas[0]["updated_at"]),
                         datetime.fromtimestamp(now, timezone.utc).date().isoformat())
        self.assertEqual(board[0]["published_at"], "2026-11-04T10:00:00Z")
        self.assertEqual(board[0]["company"], "Exemplo")

    def test_panel_requires_login_and_csrf(self):
        with patch.dict(os.environ, {"PLATFORM_PERSON": "glaucojunior",
                                     "PLATFORM_USER": "glauco", "PLATFORM_PASSWORD": "test-only-secret"}):
            client = TestClient(app)
            self.assertEqual(client.get("/").status_code, 401)
            self.assertEqual(client.get("/", auth=("glauco", "test-only-secret")).status_code, 200)
            self.assertEqual(client.post("/run", auth=("glauco", "test-only-secret"),
                                         data={"csrf": "wrong"}).status_code, 403)

    def test_panel_status_is_manual_and_documents_are_private(self):
        output = self.root / "outputs" / "glaucojunior" / "platform"
        con = core.database(output)
        core.import_jobs(con, [sources.job(
            "manual", "https://empresa.gupy.io/jobs/123", "DevOps", "Empresa",
            "Remoto Brasil", "Terraform")], POLICY)
        identity = con.execute("SELECT id FROM jobs").fetchone()[0]
        con.close()
        with patch.dict(os.environ, {"PLATFORM_PERSON": "glaucojunior",
                                     "PLATFORM_USER": "glauco", "PLATFORM_PASSWORD": "test-only-secret"}):
            client = TestClient(app)
            self.assertEqual(client.get(f"/jobs/{identity}/resume.pdf").status_code, 401)
            result = client.post(f"/jobs/{identity}/status",
                                 auth=("glauco", "test-only-secret"),
                                 data={"csrf": token(), "status": "avaliar", "note": "Vou revisar"},
                                 follow_redirects=False)
            self.assertEqual(result.status_code, 303)
            con = core.database(output)
            self.assertEqual(con.execute("SELECT status, note FROM jobs").fetchone()[:],
                             ("avaliar", "Vou revisar"))
            con.close()


if __name__ == "__main__":
    unittest.main()
