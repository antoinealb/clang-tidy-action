#!/usr/bin/env python3
"""
Analyze a repository with clang-tidy.
"""

import argparse
import collections
import contextlib
import json
import os
import re
import shlex
import subprocess
import tempfile
import requests


Finding = collections.namedtuple("Finding", ["line", "text"])

@contextlib.contextmanager
def cd(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)

@contextlib.contextmanager
def bold_text():
    BOLD = "\u001b[1m"
    RESET = "\u001b[0m"
    print(BOLD, end='')
    try:
        yield
    finally:
        print(RESET, end='')


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_path")
    parser.add_argument("--config", "-c", help="Path to the JSON config file", required=True, type=argparse.FileType())

    return parser.parse_args()


def find_repo_files():
    cmd = "git ls-tree --full-tree -r HEAD".split()
    files = subprocess.check_output(cmd).decode().splitlines()
    files = [f.split('\t')[1] for f in files]

    return files


def analyzable_files(files):
    """
    Returns only the files that can be used by clang-tidy.
    """
    allowed_extensions = [".c", ".cpp", ".cxx"]
    return [f for f in files if any(f.endswith(ext) for ext in allowed_extensions)]


def analyze_file(path, compile_db_path):
    cmd = "clang-tidy {} -p {}".format(path, compile_db_path)
    print(cmd)
    output = subprocess.check_output(cmd.split(), stderr=subprocess.PIPE).decode()
    findings = parse_clang_output(output)
    return findings


def cleanup_compile_db(compile_db):
    result = []
    # List of arguments that should be allowed in the final compilation DB.
    argument_whitelist = [
        '-c',
        '-D.*',
        '-W.*',
        '-I.*',
        '-o', r'.*\.o'
    ]
    for entry in compile_db:
        arguments = []

        # First copy the compiler name
        arguments.append(entry['arguments'].pop(0))

        for arg in entry['arguments']:
            if any(re.match(pattern, arg) for pattern in argument_whitelist):
                arguments.append(arg)

            # Also copy the source file arg
            elif arg == entry['file']:
                arguments.append(arg)

        # TODO(antoinealb): This is only required on my laptop because I did not install clang correctly
        arguments.append("-I~/.local/arm/arm-none-eabi/include/")

        new_entry = {
            'arguments': arguments,
            'directory': entry['directory'],
            'file': entry['file'],
        }
        result.append(new_entry)

    return result


def merge_compile_commands(*args):
    """
    Merge several compilation databases, ensuring a given file is only present
    once.
    """
    accepted_files = set()
    result = []
    for db in args:
        for f in db:
            realpath = os.path.abspath(os.path.join(f['directory'], f['file']))
            if realpath not in accepted_files:
                accepted_files.add(realpath)
                result.append(f)

    return result


def parse_clang_output(output):
    error_re = ".*:(\d+):\d+: (.*)"
    out = []
    for l in output.splitlines():
        m = re.match(error_re, l)
        if m:
            line = int(m.group(1))
            msg = m.group(2)
            out.append(Finding(line=line, text=msg))

    return out


def generate_compile_commands(repo_path, config):
    dbs = []

    for src in config['compilation_commands_sources']:
        with cd(repo_path):
            cmd = 'bash -c "{}"'.format(src['command'])
            subprocess.call(shlex.split(cmd))
            with open(src['path']) as f:
                dbs.append(cleanup_compile_db(json.load(f)))

    return merge_compile_commands(*dbs)


def install_fake_compilers(config):
    if "fake_compilers" not in config:
        return

    tooldir = os.path.abspath(os.path.dirname(__file__))
    src_file = os.path.join(tooldir, 'fake_compiler.py')

    # TODO: Delete the temp files
    tmpdir = tempfile.mkdtemp()
    for cc in config["fake_compilers"]:
        os.symlink(src_file, os.path.join(tmpdir, cc))

    # Add the temp directory to our path
    os.environ['PATH'] = tmpdir + ':' + os.environ['PATH']


def report_github_status(repo, token, sha, findings):
    print("Logging annotations to github ({}, {})".format(repo, sha))
    url = "https://api.github.com/repos/{}/check-runs".format(repo)
    annotations = []
    for path, findings in findings.items():
        for f in findings:
            annotations.append({
                'path': path,
                'annotation_level': 'warning',
                'start_line': f.line,
                'end_line': f.line,
                'message': f.text
            })

    data = {
        'name': 'clang-tidy',
        'head_sha': sha,
        'status': 'completed',
        'conclusion': 'neutral',
        'output': {
            'title': 'clang-tidy',
            'summary': 'Found {} item'.format(len(annotations)),
            'annotations': annotations
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.antiope-preview+json',
        'Authorization': 'Bearer {}'.format(token),
    }

    r = requests.post(url, json=data, headers=headers)
    print(r)
    print(r.text)


def main():
    args = parse_args()
    config = json.load(args.config)

    install_fake_compilers(config)

    cleaned_db = generate_compile_commands(args.repository_path, config)

    # TODO: Delete the temp files
    tmpdir = tempfile.mkdtemp()
    with open(os.path.join(tmpdir, 'compile_commands.json'), 'w') as compile_db_file:
        json.dump(cleaned_db, compile_db_file, indent=2)

    with cd(args.repository_path):
        files = find_repo_files()
        files = analyzable_files(files)

        findings = {}
        for file in files:
            try:
                findings[file] = analyze_file(file, compile_db_file.name)
            except:
                pass

    for file in sorted(findings.keys()):
        if not findings[file]:
            continue
        with bold_text():
            print("{}:".format(file))
        for finding in findings[file]:
            print("  {}: {}".format(finding.line, finding.text))

    if not any(findings.values()):
        print("clang-tidy did not find a single thing in your code!")

    if 'GITHUB_TOKEN' in os.environ:
        repo = os.environ['GITHUB_REPOSITORY']
        sha = os.environ['GITHUB_SHA']
        token = os.environ['GITHUB_TOKEN']
        report_github_status(repo, token, sha, findings)


if __name__ == '__main__':
    main()
