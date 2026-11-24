import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks"))
from enforce_write_boundary import check  # noqa: E402


class WriteBoundary(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.ws = self._d.name
        (Path(self.ws) / "src").mkdir()

    def tearDown(self):
        self._d.cleanup()

    def w(self, path, tool="Write"):
        return check({"tool_name": tool, "cwd": self.ws, "tool_input": {"file_path": path}})

    def b(self, cmd):
        return check({"tool_name": "Bash", "cwd": self.ws, "tool_input": {"command": cmd}})

    def test_allowed(self):
        for p in ("tests/test_a.py", "__tests__/a.js", "spec/a.rb", ".testforge/raw.log",
                  "src/test/java/FooTest.java", "TESTFORGE_REPORT.md", "src/foo.test.ts"):
            self.assertIsNone(self.w(p), p)

    def test_blocked(self):
        for p in ("src/app.py", "README.md", "testsx/a.py", "tests"):
            self.assertIsNotNone(self.w(p), p)

    def test_traversal_and_outside(self):
        self.assertIsNotNone(self.w("tests/../src/app.py"))
        self.assertIsNotNone(self.w(os.path.join(self.ws, "..", "evil.py")))

    def test_absolute_inside_allowed(self):
        self.assertIsNone(self.w(os.path.join(self.ws, "tests", "t.py")))

    def test_edit_blocked(self):
        self.assertIsNotNone(self.w("src/app.py", tool="Edit"))

    def test_bash(self):
        self.assertIsNone(self.b("pytest --junitxml=.testforge/junit.xml > .testforge/raw_output.log 2>&1"))
        self.assertIsNone(self.b("pytest 2>&1 | tee .testforge/raw.log"))
        self.assertIsNotNone(self.b("echo x > src/app.py"))
        self.assertIsNotNone(self.b("sed -i 's/a/b/' src/app.py"))
        self.assertIsNotNone(self.b("rm src/app.py"))


if __name__ == "__main__":
    unittest.main()
