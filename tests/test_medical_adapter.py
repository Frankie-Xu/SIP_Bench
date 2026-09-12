import json
import tempfile
import unittest
from pathlib import Path

from sip_bench.adapters.medical import MedicalAdapter
from scripts.run_medical_demo import run_demo


class MedicalAdapterTests(unittest.TestCase):
    def test_demo_does_not_use_labels_to_predict_heldout(self):
        manifest, runs = run_demo(Path("benchmarks/medical/cases.json"))
        heldout_t0 = [r for r in runs if r["phase"] == "T0" and r["benchmark_split"] == "heldout"]
        self.assertTrue(heldout_t0)
        self.assertTrue(all(r["metadata"]["adaptation_examples"] == 0 for r in heldout_t0))
        self.assertTrue(all("diagnosis" not in r["metadata"] for r in heldout_t0))

    def test_feedback_disagreement_is_error(self):
        result = MedicalAdapter.attribute_feedback(
            prediction="uti", diagnosis="viral_uri", feedback="I disagree with this answer"
        )
        self.assertEqual(result["category"], "diagnosis_error")

    def test_fhir_mismatched_subject_is_rejected(self):
        bundle = {"resourceType": "Bundle", "entry": [
            {"resource": {"resourceType": "Encounter", "id": "e1", "subject": {"reference": "Patient/p1"}}},
            {"resource": {"resourceType": "Condition", "id": "c1", "subject": {"reference": "Patient/p2"}, "encounter": {"reference": "Encounter/e1"}, "code": {"coding": [{"code": "x"}]}}},
        ]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as handle:
            json.dump(bundle, handle); handle.flush()
            with self.assertRaises(ValueError):
                MedicalAdapter().discover_tasks(handle.name)


if __name__ == "__main__":
    unittest.main()
