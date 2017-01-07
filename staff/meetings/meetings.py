from collections import defaultdict
from datetime import datetime
from getpass import getuser
from math import ceil
from os import listdir
from os import makedirs
from os.path import exists
from os.path import expanduser
from os.path import join
from re import compile
from shutil import copyfile
from time import strftime


def get_minutes_folder():
    return expanduser('~staff/minutes')


def ls(state=None):
    states = get_membership_status(get_current_minutes_path('bod'))
    if state:
        states = {k: v for k, v in states.items() if v == state}
    return states


def quorum():
    bod = ls(state='bod')
    return int(ceil(2 / 3 * len(bod)))


def get_template(choice):
    minutes_folder = get_minutes_folder()
    if exists(join(minutes_folder, choice, 'template')):
        return join(minutes_folder, choice, 'template')
    return join(minutes_folder, 'template')


def get_minutes_choices():
    return listdir(get_minutes_folder())


def get_current_minutes_path(choice):
    return get_minutes_path(choice, get_semester())


def get_minutes_file():
    return strftime('%Y-%m-%d')


def get_minutes_path(choice, semester):
    path = join(get_minutes_folder(), choice)
    if not exists(path):
        raise ValueError('argument must be from get_minutes_choices()')
    path = join(path, semester)
    if not exists(path):
        makedirs(path)
    return path


def get_semester():
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    AUG = 9
    MAY = 5
    # a reasonable approximation for semesters
    if month > AUG or (month == AUG and day > 20):
        sem = 'Fall'
    elif month < MAY or (month == MAY and day < 20):
        sem = 'Spring'
    else:
        sem = 'Summer'
    return join(str(year), sem)


def get_minutes(folder):
    """Gets the minutes contained in a folder

    Returns the files in a folder that are the format ####.##.## exactly.
    This is done to excluse extra files that are uploaded like pdfs and
    membership file

    Args:
        folder (str): The folder the function looks through

    Returns:
        list: The sorted list of minutes files in the folder

    """
    pattern = compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
    return sorted([i for i in listdir(folder) if pattern.match(i)])


def attendance(path):
    attended = set()
    with open(path) as f:
        lines = f.read().splitlines()
        i = lines.index('Attendance:') + 1
        while lines[i] and len(lines[i].split()) == 1:
            attended.add(lines[i])
            i += 1
    return attended


def new_semester():
    year, semester = get_semester().split('/')
    sem_map = {'Spring': 'Fall', 'Fall': 'Spring'}
    year_map = {'Spring': -1, 'Fall': 0}
    last_sem = join(str(int(year) + year_map[semester]),
                    sem_map[semester])
    old_file = join(get_minutes_path('bod', last_sem), 'membership')
    new_file = join(get_current_minutes_path('bod'), 'membership')
    copyfile(old_file, new_file)


def get_membership_status(folder):
    path = join(folder, 'membership')
    if not exists(path):
        new_semester()
    status = defaultdict(int)
    with open(path) as f:
        for line in f:
            user, state = line.split()
            status[user] = state
    return status


def minutes_setup(notes, choice):
    if not exists(notes):
        copyfile(get_template(choice), notes)
    with open(notes, 'r') as f:
        s = f.read()
    s = s.replace('<USERNAME>', getuser())
    s = s.replace('<START TIME>', strftime('%H:%M'))
    if choice == 'bod':
        s = s.replace('<QUORUM>', str(quorum()))
    with open(notes, 'w') as f:
        f.write(s)


def minutes_done(notes, choice):
    with open(notes, 'r') as f:
        s = f.read()
    s = s.replace('<END TIME>', strftime('%H:%M'))
    with open(notes, 'w') as f:
        f.write(s)
    if choice == 'bod':
        update_membership()


def update_membership(semester=get_semester()):
    path = get_minutes_path('bod', semester)
    minutes = get_minutes(path)
    cur_status = get_membership_status(path)
    new_status = defaultdict(int)
    last_attended = defaultdict(lambda: '1989-02-16')
    for m in minutes:
        users = attendance(join(path, m))
        for user in users:
            last_attended[user] = m
            new_status[user] += 1

    special = {k: v for k, v in cur_status.items() if type(v) is not int}
    for user in {k: v for k, v in special.items() if v == 'offbod'}:
        special[user] = 'bod'
    new_status.update(special)
    eligible = {k: v for k, v in new_status.items() if type(v) is int and
                v >= 4 and last_attended[k] == minutes[-1]}
    for user in eligible:
        print(user + ' is eligible to join bod, would they like to join?(y/n)')
        ans = input()
        if ans == 'y' or ans == 'yes':
            new_status[user] = 'bod'

    bod = {k: v for k, v in new_status.items() if v == 'bod'}
    if len(minutes) > 0:
        cutoff = minutes[-1]
        for user in bod:
            if last_attended[user] < cutoff:
                new_status[user] = 'offbod'
    s = ''
    for user in new_status:
        s += user + ' ' + str(new_status[user]) + '\n'
    with open(join(path, 'membership'), 'w') as f:
        f.write(s)
