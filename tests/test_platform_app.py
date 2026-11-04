import json
import os
import tempfile
import unittest
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
            "greenhouse_boards": [], "lever_sites": [], "gmail_query": "",
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
            "description": "<p>Terraform &amp; Linux</p>"}]}):
            base = self.root / "input" / "glaucojunior"
            base.mkdir(parents=True)
            jobs = sources.remotive(base)
            self.assertEqual(jobs[0]["description"], "Terraform & Linux")
            self.assertIn("Remoto", jobs[0]["location"])
            self.assertEqual(len(sources.remotive(base)), 1)  # cache, sem nova requisição

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
