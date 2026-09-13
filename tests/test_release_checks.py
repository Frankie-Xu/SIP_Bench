from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.run_release_checks import (
    OPTIONAL_HISTORICAL_ARTIFACTS,
    REQUIRED_RELEASE_SCHEMA_ASSETS,
    release_artifact_gate,
)


class ReleaseArtifactGateTests(unittest.TestCase):
    def _write(self, root: Path, path: Path) -> None:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n", encoding="utf-8")

    def test_missing_required_asset_fails_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for path in REQUIRED_RELEASE_SCHEMA_ASSETS[1:]:
                self._write(root, path)
            gate = release_artifact_gate(root)
        self.assertFalse(gate["required_schema_assets_present"])
        self.assertEqual(gate["missing_required"], [str(REQUIRED_RELEASE_SCHEMA_ASSETS[0])])

    def test_missing_optional_history_is_reported_without_failing_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for path in REQUIRED_RELEASE_SCHEMA_ASSETS:
                self._write(root, path)
            gate = release_artifact_gate(root)
        self.assertTrue(gate["required_schema_assets_present"])
        self.assertEqual(gate["missing_optional_historical"], [str(path) for path in OPTIONAL_HISTORICAL_ARTIFACTS])
