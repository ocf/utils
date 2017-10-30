import bisect
import os
import os.path
import re
import time
from datetime import datetime
from os.path import join


def get_minutes_folder():
    """Returns the path to the folder containing minutes.

    Note that bod (which is stored in public_html, as they are readable on the
    Web) is symlinked in this folder.
    """
    return os.path.expanduser('~staff/minutes')


def get_minutes_choices():
    """Returns the choices available for meeting type."""
    return os.listdir(get_minutes_folder())


def get_template(choice):
    """Returns the path to the template for the given meeting type."""
    minutes_folder = get_minutes_folder()
    if os.path.exists(join(minutes_folder, choice, 'template')):
        return join(minutes_folder, choice, 'template')
    return join(minutes_folder, 'template')


def get_semester(date=None):
    """Returns the directory name for the current semester

    For example: 2017/Fall
    """
    date = date or datetime.today().date()
    year = date.year
    month = date.month
    day = date.day

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


def get_minutes_path(choice, semester=get_semester()):
    """Gets the path to the minutes directory for the given type and semester.
    """
    path = join(get_minutes_folder(), choice)
    if not os.path.exists(path):
        raise ValueError('argument must be from get_minutes_choices()')
    path = join(path, semester)
    if not os.path.exists(path):
        prev_umask = os.umask(0)
        try:
            os.makedirs(path, mode=0o2775)
        finally:
            os.umask(prev_umask)
    return path


def get_minutes_filename():
    """Gets the filename for the current minutes."""
    return time.strftime('%Y-%m-%d')


def get_minutes(folder):
    """Gets the minutes contained in a folder

    Returns the files in a folder that are the format ####-##-## exactly.
    This is done to exclude extra files that are uploaded like pdfs.

    Args:
        folder (str): The folder the function looks through

    Returns:
        list: The sorted list of minutes files in the folder

    """
    pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
    return sorted(i for i in os.listdir(folder) if pattern.match(i))


def get_prev_meeting(choice, semester, date):
    """Gets the semester and minutes filename of the last meeting of the given
    type which occurred strictly before the given date.

    Args:
        choice: the meeting type
        semester: the directory name (as given by ``meetings.get_semester()``)
                  for the semester in which the meeting took place
        date: a datetime.date object

    Returns:
        A tuple of (semester of previous meeting, filename of previous meeting
        minutes)

    """
    minutes = [datetime.strptime(m, '%Y-%m-%d').date()
               for m in get_minutes(get_minutes_path(choice, semester=semester))]
    i = bisect.bisect_left(minutes, date)
    if i > 0:
        semester_prev = semester
        prev_meeting_filename = minutes[i - 1].strftime('%Y-%m-%d')
    else:
        semester_prev = get_prev_semester(semester=semester)
        strarr_prev_minutes = get_minutes(get_minutes_path(choice,
                                                           semester=semester_prev))
        prev_meeting_filename = strarr_prev_minutes[-1]

    return (semester_prev, prev_meeting_filename)


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
