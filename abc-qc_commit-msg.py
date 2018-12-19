#!/usr/bin/env python2.7
import sys
import re

msg_file = open(sys.argv[1], 'r')
msg = msg_file.read()

msg_ln_split = msg.split('\n')
commit_msg_without_cmt = [msg_line for msg_line in msg.split('\n') if not re.findall(r"^#", msg_line)]
commit_errors = False
if len(commit_msg_without_cmt) > 0:
    #Limit the subject line to 50 characters
    print '\033[01;31m'
    if len(commit_msg_without_cmt[0]) > 50:
        print('The subject line should be limited to 50 characters.')
        commit_errors = True
    #Capitalize the subject line
    if len(commit_msg_without_cmt[0]) > 1:
        if commit_msg_without_cmt[0][0].islower():
            print('Subject line should begin with capital letter.')
            commit_errors = True
        if commit_msg_without_cmt[0].strip()[-1] == '.':
            print('Subject line should not end with a full stop.')
            commit_errors = True
        if len(commit_msg_without_cmt) > 2:
            if commit_msg_without_cmt[1] != '':
                print('Subject line and body should be seperated with a blank line.')
                commit_errors = True
            if len(commit_msg_without_cmt) > 3:
                body_overflowed_lst = [body_line for body_line in commit_msg_without_cmt[2:len(commit_msg_without_cmt)] if len(body_line) > 72]
                if body_overflowed_lst:
                    commit_errors = True
                    print("This lines of body are over 72 characters:\n")
                    for overflowed_line in body_overflowed_lst:
                        print(overflowed_line)
print '\033[0m'
if commit_errors == True:
    sys.exit(1)
else:
    sys.exit(0)