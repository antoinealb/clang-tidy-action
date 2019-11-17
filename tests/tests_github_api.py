import unittest
import unittest.mock
import analyze


class GithubApiTestCase(unittest.TestCase):
    @unittest.mock.patch('requests.post')
    def test_create_check(self, post):
        sha = 'foobar'
        repo = 'antoinealb/foobar'
        token = 'secret'
        findings = {'test/main.c': [analyze.Finding(text='foobar', line=283)]}
        analyze.report_github_status(repo, token, sha, findings)

        expected_data = {
            'name': 'clang-tidy',
            'head_sha': sha,
            'status': 'completed',
            'conclusion': 'neutral',
            'output': {
                'title': 'clang-tidy',
                'summary': 'Found 1 item',
                'annotations': [{
                    'path': 'test/main.c',
                    'start_line': 283,
                    'end_line': 283,
                    'annotation_level': 'warning',
                    'message': 'foobar'
                }]
            }
        }

        expected_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.antiope-preview+json',
            'Authorization': 'Bearer secret',
        }

        url = 'https://api.github.com/repos/antoinealb/foobar/check-runs'
        post.assert_any_call(url, data=expected_data, headers=expected_headers)

