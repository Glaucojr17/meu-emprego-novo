import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.opportunities.tracker import canonical_url, from_eml, read_ledger, record, scan, score


class OpportunityTests(unittest.TestCase):
    def test_links_only_direct_job_hosts(self):
        self.assertEqual(canonical_url("https://www.linkedin.com/jobs/view/123/?trk=mail"),
                         "https://www.linkedin.com/jobs/view/123/")
        self.assertEqual(canonical_url("https://example.gupy.io/jobs/456?source=mail"),
                         "https://example.gupy.io/jobs/456")
        self.assertIsNone(canonical_url("https://linkedin.com.evil.test/jobs/view/123"))
        self.assertIsNone(canonical_url("http://example.gupy.io/jobs/456"))

    def test_alert_parses_anchor_and_deduplicates_with_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            alerts = root / "alerts"
            alerts.mkdir()
            (alerts / "one.eml").write_bytes(
                b"Subject: Oportunidades DevOps\nMIME-Version: 1.0\nContent-Type: text/html; charset=utf-8\n\n"
                b'<a href="https://empresa.gupy.io/jobs/456?source=email">DevOps remoto Terraform</a>'
            )
            self.assertEqual(from_eml(alerts / "one.eml")[0]["title"], "DevOps remoto Terraform")
            (root / "vagas.csv").write_text(
                "source,url,title,company,location,description\n"
                "manual,https://empresa.gupy.io/jobs/456,DevOps,Empresa,Remoto,Terraform\n",
                encoding="utf-8")
            (root / "policy.json").write_text(json.dumps({
                "titles": ["DevOps"], "skills": ["Terraform"],
                "exclude": ["presencial"], "remote_only": True}), encoding="utf-8")
            args = SimpleNamespace(alerts=alerts, csv=root / "vagas.csv",
                                   policy=root / "policy.json", output=root / "output")
            scan(args)
            report = (args.output / "relatorio.md").read_text(encoding="utf-8")
            self.assertEqual(report.count("## DevOps"), 1)
            self.assertIn("Nenhuma candidatura confirmada", report)

    def test_remote_requires_explicit_evidence_and_manual_submission(self):
        policy = {"titles": ["SRE"], "skills": ["Kubernetes"], "exclude": [], "remote_only": True}
        job = {"title": "SRE", "description": "Kubernetes", "location": "", "company": ""}
        self.assertFalse(score(job, policy)["eligible"])
        job["location"] = "Remoto"
        self.assertTrue(score(job, policy)["eligible"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = SimpleNamespace(url="https://www.linkedin.com/jobs/view/123", title="SRE",
                                   evidence=root / "missing.png", output=root / "output")
            with self.assertRaises(ValueError):
                record(args)
            self.assertEqual(read_ledger(args.output / "historico.json"), {})
            args.evidence.write_bytes(b"recibo de exemplo")
            record(args)
            entry = read_ledger(args.output / "historico.json")[
                "https://www.linkedin.com/jobs/view/123/"
            ]
            self.assertEqual(entry["status"], "candidatada")


if __name__ == "__main__":
    unittest.main()
