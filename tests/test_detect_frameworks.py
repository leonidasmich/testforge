import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from detect_frameworks import detect_frameworks  # noqa: E402


def detect(files):
    with tempfile.TemporaryDirectory() as d:
        for name, text in files.items():
            (Path(d) / name).write_text(text, encoding="utf-8")
        return detect_frameworks(d)


class JavaDetection(unittest.TestCase):
    def test_testng_maven(self):
        r = detect({"pom.xml": "<dependency><artifactId>testng</artifactId></dependency>"})
        self.assertEqual(r["frameworks"], ["testng"])
        self.assertEqual(r["recommended_command"], "mvn test")

    def test_junit4_maven(self):
        r = detect({"pom.xml": "<groupId>junit</groupId><artifactId>junit</artifactId>"})
        self.assertIn("junit4", r["frameworks"])
        self.assertNotIn("junit5", r["frameworks"])

    def test_junit5_gradle_kts(self):
        r = detect({"build.gradle.kts": 'testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")'})
        self.assertEqual(r["frameworks"], ["junit5"])
        self.assertEqual(r["recommended_command"], "gradle test")

    def test_unknown_not_junit5(self):
        r = detect({"pom.xml": "<project></project>"})
        self.assertEqual(r["frameworks"], ["java-unknown"])
        self.assertIn("notes", r)

    def test_wrapper_preferred(self):
        r = detect({"build.gradle": "", "gradlew": ""})
        self.assertEqual(r["recommended_command"], "./gradlew test")


if __name__ == "__main__":
    unittest.main()
