import unittest
import analyze

class ClangTidyErrorParsingTestCase(unittest.TestCase):
    def test_parse_single_warning(self):
        case = """/Users/antoinealb/src/cvra/robot-software/test.c:2:13: warning: statement should be inside braces [readability-braces-around-statements]
    if (bar)
            ^
             {
        """
        result = analyze.parse_clang_output(case)
        self.assertEqual(len(result), 1, "Should contain one warning")
        self.assertEqual(result[0].line, 2, "Should be on line 2")
        self.assertEqual(result[0].text, "warning: statement should be inside braces [readability-braces-around-statements]")

    def test_parse_many_warnings(self):
        case = """/Users/antoinealb/src/cvra/robot-software/test.c:2:13: warning: statement should be inside braces [readability-braces-around-statements]
    if (bar)
            ^
             {
        """
        # We have 3 identical warnings
        result = analyze.parse_clang_output(case * 3)
        self.assertEqual(len(result), 3, "Should contain three warnings")
