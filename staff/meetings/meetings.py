import re
from collections import defaultdict
from datetime import datetime
from getpass import getuser
from math import ceil
from os import chmod
from os import listdir
from os import makedirs
from os import umask
from os.path import exists
from os.path import expanduser
from os.path import join
from shutil import copyfile
from string import Template
from time import strftime


# Max length of usernames
USERNAME_LEN = 16


def get_minutes_folder():
    """Returns the path to the folder containing minutes.

    Note that bod (which is stored in public_html, as they are readable on the
    Web) is symlinked in this folder.
    """
    return expanduser('~staff/minutes')


def ls(state='all'):
    """Lists everyone with the given membership state.

    Args:
        state: the membership state. 'all' lists all attendees regardless of
               state.

    Returns:
        A list of BoD attendees with the given membership state

    """
    states = get_bod_membership()
    if state != 'all':
        states = {k: v for k, v in states.items() if v == state}
    return states


def quorum():
    """Returns the quorum for this BoD meeting."""
    bod = ls(state='bod')
    return int(ceil(2 / 3 * len(bod)))


def get_template(choice):
    """Returns the path to the template for the given meeting type."""
    minutes_folder = get_minutes_folder()
    if exists(join(minutes_folder, choice, 'template')):
        return join(minutes_folder, choice, 'template')
    return join(minutes_folder, 'template')


def get_minutes_choices():
    """Returns the choices available for meeting type."""
    return listdir(get_minutes_folder())


def get_semester():
    """Returns the directory name for the current semester

    For example: 2017/Fall
    """
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    AUG = 8
    MAY = 5
    # a reasonable approximation for semesters
    if month > AUG or (month == AUG and day > 20):
        sem = 'Fall'
    elif month < MAY or (month == MAY and day < 20):
        sem = 'Spring'
    else:
        sem = 'Summer'
    return join(str(year), sem)


def get_bod_minutes_path(semester=get_semester()):
    """Gets the path to the BoD minutes directory for the given semester."""
    return get_minutes_path('bod', semester=semester)


def get_minutes_path(choice, semester=get_semester()):
    """Gets the path to the minutes directory for the given type and semester.
    """
    path = join(get_minutes_folder(), choice)
    if not exists(path):
        raise ValueError('argument must be from get_minutes_choices()')
    path = join(path, semester)
    if not exists(path):
        prev_umask = umask(0)
        try:
            makedirs(path, mode=0o2775)
        finally:
            umask(prev_umask)
    return path


def get_minutes_file():
    """Gets the filename for the current minutes."""
    return strftime('%Y-%m-%d')


def get_bod_membership_file(semester=get_semester()):
    """Gets the BoD membership file for the given semester."""
    folder = get_bod_minutes_path(semester=semester)
    path = join(folder, 'membership')
    return path


def get_bod_membership(semester=get_semester()):
    """Get the membership status for every BoD attendee for the given semester.

    Args:
        semester: The specified semester. Defaults to the current semester.

    Returns:
        A dictionary of (attendee, state) mappings.
    """
    status = defaultdict(int)
    path = get_bod_membership_file(semester=semester)
    if not exists(path):
        new_semester()
    with open(path) as f:
        for line in f:
            user, state = line.split()
            status[user] = state
    return status


def get_minutes(folder):
    """Gets the minutes contained in a folder

    Returns the files in a folder that are the format ####-##-## exactly.
    This is done to excluse extra files that are uploaded like pdfs and
    membership file

    Args:
        folder (str): The folder the function looks through

    Returns:
        list: The sorted list of minutes files in the folder

    """
    pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
    return sorted(i for i in listdir(folder) if pattern.match(i))


def get_attendance(path):
    """Returns the set of attendees for the given meeting.

    Args:
        path: path to the minutes file for the desired meeting

    Returns:
        A set containing the usernames of everyone who attended that meeting

    """
    attended = set()
    with open(path) as f:
        lines = f.read().splitlines()
        i = lines.index('Attendance:') + 1
        while lines[i] and len(lines[i].split()) == 1:
            attended.add(lines[i])
            i += 1
    return attended


def get_prev_semester(semester=get_semester()):
    """Returns the path for the semester before the given semester.

    >>> get_prev_semester('2017/Fall')
    '2017/Spring'
    >>> get_prev_semester('2017/Spring')
    '2016/Fall'
    """
    year, sem = semester.split('/')
    if sem == 'Spring':
        return join(str(int(year) - 1), 'Fall')
    else:
        return join(year, 'Spring')


def new_semester():
    """Sets up a semester's directory.

    Currently copies the BoD membership file from the previous semester.
    """
    new_file = get_bod_membership_file()
    old_file = get_bod_membership_file(semester=get_prev_semester())
    copyfile(old_file, new_file)
    chmod(new_file, 0o664)


def minutes_setup(notes, choice):
    # Create minutes file from template if it doesn't exist
    if not exists(notes):
        copyfile(get_template(choice), notes)
        chmod(notes, 0o644)

    with open(notes, 'r') as f:
        s = Template(f.read())

    # Substitute values
    subs = {'username': getuser(), 'start_time': strftime('%H:%M')}
    if choice == 'bod':
        subs['quorum'] = str(quorum())
    s = s.safe_substitute(subs)

    # Write out file with substituted values
    with open(notes, 'w') as f:
        f.write(s)


def minutes_done(notes, choice):
    # Substitute in ending values
    with open(notes, 'r') as f:
        s = Template(f.read())
    s = s.safe_substitute(end_time=strftime('%H:%M'))

    # Write out file with substituted values
    with open(notes, 'w') as f:
        f.write(s)

    if choice == 'bod':
        update_membership()


def update_membership():
    """Updates the membership file for the current semester.

    Uses the attendance list for the current meeting to update the membership
    file for the current semester.
    """
    cur_status = get_bod_membership()
    bod_members = {member for member, status in cur_status.items()
                   if status == 'bod'}

    minutes_path = get_bod_minutes_path()
    minutes_files = get_minutes(minutes_path)
    if minutes_files:
        print(join(minutes_path, minutes_files[-1]))
        attendees_today = get_attendance(join(minutes_path, minutes_files[-1]))

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
        print(join(minutes_path, minutes_files[-2]))
        attended_last_meeting = get_attendance(join(minutes_path,
                                                    minutes_files[-2]))
    else:
        last_semester_minutes_path = get_bod_minutes_path(get_prev_semester())
        last_semester_minutes = get_minutes(last_semester_minutes_path)
        assert len(last_semester_minutes) > 1, \
            'Expecting at least one BoD meeting last semester'
        attended_last_meeting = get_attendance(join(last_semester_minutes_path,
                                                    last_semester_minutes[-1]))

    print(attendees_today)
    print(attended_last_meeting)
    for non_attendee in bod_members - (attendees_today | attended_last_meeting):
        print(non_attendee, 'is being kicked off bod')
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

    with open(get_bod_membership_file(), 'w') as f:
        f.write(str_new_status)
