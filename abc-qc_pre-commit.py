#!/usr/bin/env python2.7
import subprocess
import re
import sys

p = subprocess.Popen('git diff --cached --name-only --diff-filter=ACM', stdout=subprocess.PIPE, shell=True)
(git_diff_files, git_diff_files_err) = p.communicate()
git_diff_status = p.wait()
if not git_diff_files:
    print '\033[01;35m'
    print 'No staged files'
    print '\033[0m'
    sys.exit(0)

git_diff_files = [git_diff_files for git_diff_files in git_diff_files.split('\n') if git_diff_files]
js_changed_files = []
py_changed_files = []
for git_diff_file in git_diff_files:
    regex_js = re.search('(.*[.]js)', git_diff_file)
    if regex_js:
        js_changed_files.append(regex_js.group(1))
    regex_py = re.search('(.*[.]py)', git_diff_file)
    if regex_py:
        py_changed_files.append(regex_py.group(1))

p = subprocess.Popen('which flake8 &> /dev/null', stdout=subprocess.PIPE, shell=True)
(flake8_check, flake8_check_err) = p.communicate()
flake8_check_status = p.wait()
if flake8_check_status != 0:
    print '\033[01;31m'
    print "Flake 8 is not installed\nContinuing without flake8 test"
    print '\033[0m'

if flake8_check_status == 0:
    p = subprocess.Popen('git diff --cached -U0 | flake8 --diff', stdout=subprocess.PIPE, shell=True)
    (flake8_errors, flake8_errors_err) = p.communicate()
    flake8_errors_status = p.wait()
else:
    flake8_errors_status = 0

py_warning = {}
for py_changed_file in py_changed_files:
    p = subprocess.Popen('git diff --cached -U0 ' + py_changed_file, stdout=subprocess.PIPE, shell=True)
    (git_diff_file_details, git_diff_file_details_err) = p.communicate()
    git_diff_file_details_status = p.wait()
    git_diff_file_details_lst = git_diff_file_details.split("\n")

    py_error_single_line_lst = []
    py_error_line_combined_lst = []
    for i in git_diff_file_details_lst:
        if not re.findall(r'@@.*[+][0-9]*[,]*[0-9]*\s*@@', i):
            py_error_single_line_lst.append(i)
        else:
            py_error_line_combined_lst.append('\n'.join(py_error_single_line_lst))
            py_error_single_line_lst = []
            py_error_single_line_lst.append(i)
    py_error_line_combined_lst.append('\n'.join(py_error_single_line_lst))
    py_to_be_warned_lst = [each_py_change for each_py_change in py_error_line_combined_lst if re.findall(r'@@.*[+]([0-9]*)[,]*([0-9]*)\s*@@', each_py_change) and re.findall(r'pudb', each_py_change)]
    if py_to_be_warned_lst:
        py_warning[py_changed_file] = py_to_be_warned_lst

if flake8_check_status == 0 and flake8_errors_status != 0:
    print '\033[01;31m'
    print "Flake8 errors:"
    print ''
    print flake8_errors
    print '\033[0m'
    if not py_warning:
        print '-----------------------------------------------------------------'

if py_warning:
    print '\033[01;35m'
    print "Python warnings:"
    print ''
    for file in py_warning:
        print '-> ' + file
        print ''
        for py_warning_lines in py_warning[file]:
            print py_warning_lines
    print ''
    print '\033[0m'
    print '-----------------------------------------------------------------'

p = subprocess.Popen('which eslint &> /dev/null', stdout=subprocess.PIPE, shell=True)
(eslint_check, eslint_check_err) = p.communicate()
eslint_check_status = p.wait()
if eslint_check_status != 0:
    print '\033[01;31m'
    print "ESlint is not installed\nContinuing without ESLint test"
    print '\033[0m'

eslint_errors = {}
eslint_warning = {}
for js_changed_file in js_changed_files:
    if eslint_check_status == 0:
        p = subprocess.Popen('eslint ' + js_changed_file, stdout=subprocess.PIPE, shell=True)
        (eslint_file_check_results, eslint_file_check_results_err) = p.communicate()
        eslint_file_check_results_status = p.wait()
        eslint_file_check_results_lst = [eslint_file_check_result for eslint_file_check_result in eslint_file_check_results.split("\n") if re.findall(r"\s*[0-9]*:[0-9]*\s*error", eslint_file_check_result)]
        eslint_error_line_lst = set()
        for eslint_file_check_result in eslint_file_check_results_lst:
            m = re.search(r'\s*([0-9]*):[0-9]*\s*error', eslint_file_check_result)
            if m:
                found = m.group(1)
                eslint_error_line_lst.add(found)

    p = subprocess.Popen('git diff --cached -U0 ' + js_changed_file, stdout=subprocess.PIPE, shell=True)
    (git_diff_file_details, git_diff_file_details_err) = p.communicate()
    git_diff_file_details_status = p.wait()
    git_diff_file_details_lst = git_diff_file_details.split("\n")

    js_error_single_line_lst = []
    js_error_line_combined_lst = []
    for i in git_diff_file_details_lst:
        if not re.findall(r'@@.*[+][0-9]*[,]*[0-9]*\s*@@', i):
            js_error_single_line_lst.append(i)
        else:
            js_error_line_combined_lst.append('\n'.join(js_error_single_line_lst))
            js_error_single_line_lst = []
            js_error_single_line_lst.append(i)
    js_error_line_combined_lst.append('\n'.join(js_error_single_line_lst))
    js_to_be_warned_lst = [each_js_change for each_js_change in js_error_line_combined_lst if re.findall(r'@@.*[+]([0-9]*)[,]*([0-9]*)\s*@@', each_js_change) and re.findall(r'alert[(].*[)]', each_js_change)]
    if js_to_be_warned_lst:
        eslint_warning[js_changed_file] = js_to_be_warned_lst

    if eslint_check_status == 0:
        git_diff_changed_line_lst = [git_diff_file_detail for git_diff_file_detail in git_diff_file_details_lst if re.findall(r'@@.*[+]([0-9]*)[,]*([0-9]*)\s*@@', git_diff_file_detail)]
        lines_changed = set()
        for git_diff_changed_line in git_diff_changed_line_lst:
            m = re.search(r'@@.*[+]([0-9]*)[,]*([0-9]*)\s*@@', git_diff_changed_line)
            if m:
                found = m.group(1)
                no = 0 if m.group(2) == '' else int(m.group(2))
                lines_changed.add(found)
                for i in range(no):
                    lines_changed.add(str(int(found) + i))

        our_js_lines_with_error = lines_changed.intersection(eslint_error_line_lst)
        if our_js_lines_with_error:
            our_error_lst = [eslint_file_check_result for eslint_file_check_result in eslint_file_check_results.split("\n") if re.findall(r'(?:' + ('|'.join(list(map(str, list(our_js_lines_with_error))))) + '):[0-9]*\s*error', eslint_file_check_result)]
        if our_js_lines_with_error and our_error_lst:
            eslint_errors[js_changed_file] = our_error_lst


if eslint_check_status == 0 and eslint_errors:
    print '\033[01;31m'
    print "ESlint errors:"
    print ''
    for file in eslint_errors:
        print '-> ' + file
        print ''
        for eslint_error_lines in eslint_errors[file]:
            print eslint_error_lines
        print ''
    print '\033[0m'
    print ''
else:
    eslint_errors = False

if eslint_warning:
    print '\033[01;35m'
    print "Javascript warning:"
    print ''
    for file in eslint_warning:
        print '-> ' + file
        print ''
        for eslint_warning_lines in eslint_warning[file]:
            print eslint_warning_lines
        print ''
    print '\033[0m'
    print ''

if eslint_errors or flake8_errors_status != 0:
    sys.exit(1)
else:
    sys.exit(0)