"""Module for BoD meeting logic."""
import os
import shutil
from collections import defaultdict
from math import ceil
from os.path import join

import meetings


# Max length of usernames
USERNAME_LEN = 16


def ls(state='all'):
    """Lists everyone with the given membership state.

    Args:
        state: the membership state. 'all' lists all attendees regardless of
               state.

    Returns:
        A list of BoD attendees with the given membership state

    """
    states = get_membership()
    if state != 'all':
        states = {k: v for k, v in states.items() if v == state}
    return states


def quorum():
    """Returns the quorum for this BoD meeting."""
    bod = ls(state='bod')
    return int(ceil(2 / 3 * len(bod)))


def get_bod_minutes_path(semester=meetings.get_semester()):
    """Gets the path to the BoD minutes directory for the given semester."""
    return meetings.get_minutes_path('bod', semester=semester)


def get_membership_file(semester=meetings.get_semester()):
    """Gets the BoD membership file for the given semester."""
    folder = get_bod_minutes_path(semester=semester)
    path = join(folder, 'membership')
    return path


def get_membership(semester=meetings.get_semester()):
    """Get the membership status for every BoD attendee for the given semester.

    Args:
        semester: The specified semester. Defaults to the current semester.

    Returns:
        A dictionary of (attendee, state) mappings.
    """
    status = defaultdict(int)
    path = get_membership_file(semester=semester)
    if not os.path.exists(path):
        handle_new_semester()
    with open(path) as f:
        for line in f:
            user, state = line.split()
            status[user] = state
    return status


def handle_new_semester():
    """Sets up a semester's directory.

    Currently copies the BoD membership file from the previous semester.
    """
    new_file = get_membership_file()
    old_file = get_membership_file(semester=meetings.get_prev_semester())
    shutil.copyfile(old_file, new_file)
    os.chmod(new_file, 0o664)


def update_membership():
    """Updates the membership file for the current semester.

    Uses the attendance list for the current meeting to update the membership
    file for the current semester.
    """
    cur_status = get_membership()
    bod_members = {member for member, status in cur_status.items()
                   if status == 'bod'}

    minutes_path = get_bod_minutes_path()
    minutes_files = meetings.get_minutes(minutes_path)
    if minutes_files:
        attendees_today = meetings.get_attendance(join(minutes_path,
                                                       minutes_files[-1]))

    # Start new status dict. Begin by adding all BoD members.
    new_status = {member: status for member, status in cur_status.items()
                  if status == 'bod'}

    # Add new members to BoD
    guests = attendees_today - bod_members
    for attendee in guests:
        reply = input(attendee + ' is not on BoD. Would they like to join? '
                      '(y/n) ')
        if reply == 'y' or reply == 'yes':
            new_status[attendee] = 'bod'

    # Kick people off BoD if they haven't come to the previous 2 meetings
    # (including the current one)
    if len(minutes_files) >= 2:
        attended_last_meeting = meetings.get_attendance(join(minutes_path,
                                                             minutes_files[-2]))
    else:
        last_semester_minutes_path = get_bod_minutes_path(
            meetings.get_prev_semester())
        last_semester_minutes = meetings.get_minutes(last_semester_minutes_path)
        assert len(last_semester_minutes) > 1, \
            'Expecting at least one BoD meeting last semester'
        attended_last_meeting = meetings.get_attendance(
            join(last_semester_minutes_path, last_semester_minutes[-1]))

    for non_attendee in bod_members - (attendees_today | attended_last_meeting):
        del new_status[non_attendee]

    # Write out new status
    def membership_key(p):
        special = {'bod': 0, 'offbod': 1}
        u, s = p
        if s in special:
            s = special[s]
        return (s, u)
    sorted_new_status = sorted(new_status.items(), key=membership_key)
    str_new_status = ''.join('{}  {}\n'.format(attendee.ljust(USERNAME_LEN),
                                               status)
                             for attendee, status in sorted_new_status)

    with open(get_membership_file(), 'w') as f:
        f.write(str_new_status)
