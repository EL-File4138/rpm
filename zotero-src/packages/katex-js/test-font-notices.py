import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "font_notices", Path(__file__).with_name("collect-font-notices.py"))
notices = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notices)


class FontNoticeTest(unittest.TestCase):
    def pfb(self):
        header = (b"%!PS-AdobeFont-1.0\n%Copyright: American Mathematical Society\n"
                  b"% SIL Open Font License\n%%EndComments\n/EncryptedLater true def\n")
        return b"\x80\x01" + len(header).to_bytes(4, "little") + header

    def test_only_authentic_ascii_notice_is_retained(self):
        notice = notices.pfb_notice(self.pfb())
        self.assertIn(b"%Copyright: American Mathematical Society\n", notice)
        self.assertTrue(notice.endswith(b"%%EndComments\n"))
        self.assertNotIn(b"EncryptedLater", notice)

    def test_malformed_or_missing_notices_fail(self):
        for data in (b"not PFB", self.pfb()[:10],
                     self.pfb().replace(b"%Copyright:", b"%Unrelated:")):
            with self.assertRaises(ValueError):
                notices.pfb_notice(data)

    def test_actual_inputs_are_copied_without_font_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "cmr10.mf").write_bytes(b"% Knuth notice\nunchanged source\n")
            for name in ("eufm10", "eufb10"):
                (root / (name + ".pfb")).write_bytes(self.pfb())
            with patch.object(notices.subprocess, "check_output",
                              side_effect=lambda command, **kwargs: str(root / command[1])):
                notices.collect(root / "notices")
            self.assertEqual((root / "notices/cmr10.mf").read_bytes(),
                             (root / "cmr10.mf").read_bytes())
            self.assertEqual((root / "notices/eufm10-notice.txt").read_bytes(),
                             notices.pfb_notice(self.pfb()))


if __name__ == "__main__":
    unittest.main()
