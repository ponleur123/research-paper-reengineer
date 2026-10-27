"""Static skill-contract checks; these do not certify scientific reproduction quality."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
PROTOCOL = (ROOT / "references" / "reproduction.md").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")

class ModeContractTests(unittest.TestCase):
    def test_version_and_modes(self):
        self.assertRegex(SKILL, r'version: "1\.1\.0"')
        for mode in ("analyze", "reconstruct", "reproduce", "blind-reproduce", "audit"):
            self.assertIn("`" + mode + "`", SKILL)
            self.assertIn("`" + mode + "`", README)

    def test_blind_source_exclusion(self):
        blind = SKILL.split("| `blind-reproduce` |")[1].split("| `audit` |")[0]
        self.assertIn("never inspect", blind.lower())
        for term in ("original", "third-party", "checkpoints"):
            self.assertIn(term, PROTOCOL.lower())
        self.assertIn("Prohibited", PROTOCOL)
        self.assertIn("frozen", PROTOCOL)

    def test_real_data_and_provenance(self):
        for token in ("real dataset", "train", "checkpoint", "validation", "test"):
            self.assertIn(token, PROTOCOL.lower())
        for token in ("G0", "G1", "G2", "G3", "G4"):
            self.assertIn(token, PROTOCOL)
        self.assertIn("Do not tune against the final test partition", PROTOCOL)
        self.assertIn("never a successful benchmark reproduction", SKILL)

    def test_short_prompt_and_docs(self):
        self.assertIn("Short-prompt contract", SKILL)
        self.assertIn("Paper: https://arxiv.org/abs/1608.06037", README)
        self.assertIn("references/reproduction.md", SKILL)

if __name__ == "__main__":
    unittest.main()
