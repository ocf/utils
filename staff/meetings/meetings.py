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
from string import Template
from time import strftime


def get_minutes_folder():
    return expanduser('~staff/minutes')


def ls(state='all'):
    states = get_bod_membership()
    if state != 'all':
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


def get_bod_minutes_path(semester=get_semester()):
    return get_minutes_path('bod', semester=semester)


def get_minutes_path(choice, semester=get_semester()):
    path = join(get_minutes_folder(), choice)
    if not exists(path):
        raise ValueError('argument must be from get_minutes_choices()')
    path = join(path, semester)
    if not exists(path):
        makedirs(path)
    return path


def get_minutes_file():
    return strftime('%Y-%m-%d')


def get_bod_membership_file(semester=get_semester()):
    folder = get_bod_minutes_path(semester=semester)
    path = join(folder, 'membership')
    return path


def get_bod_membership(semester=get_semester()):
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
    new_file = get_bod_membership_file()
    old_file = get_bod_membership_file(semester=last_sem)
    copyfile(old_file, new_file)


def minutes_setup(notes, choice):
    if not exists(notes):
        copyfile(get_template(choice), notes)
    with open(notes, 'r') as f:
        s = Template(f.read())
    subs = {'username': getuser(), 'start_time': strftime('%H:%M')}
    if choice == 'bod':
        subs['quorum'] = str(quorum())
    s = s.safe_substitute(subs)
    with open(notes, 'w') as f:
        f.write(s)


def minutes_done(notes, choice):
    with open(notes, 'r') as f:
        s = Template(f.read())
    s = s.safe_substitute(end_time=strftime('%H:%M'))
    with open(notes, 'w') as f:
        f.write(s)
    if choice == 'bod':
        update_membership()


def membership_key(p):
    """implements reverse lexicographic order to sort user, membership status pairs"""
    special = {'offbod': 'bod', 'bod': 'offbod'}
    u, s = p
    if s in special:
        s = special[s]
    return s + u


def update_membership(semester=get_semester()):
    minutes = get_minutes(get_bod_minutes_path(semester=semester))
    cur_status = get_bod_membership()
    new_status = defaultdict(int)
    last_attended = defaultdict(lambda: '1989-02-16')
    minutes_path = get_bod_minutes_path(semester=semester)
    for m in minutes:
        users = attendance(join(minutes_path, m))
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
        print(user + ' is eligible to join bod, would they like to join? (y/n)')
        ans = input()
        if ans == 'y' or ans == 'yes':
            new_status[user] = 'bod'

    bod = {k: v for k, v in new_status.items() if v == 'bod'}
    if len(minutes) > 0:
        cutoff = minutes[-1]
        for user in bod:
            if last_attended[user] < cutoff:
                new_status[user] = 'offbod'
    new_status = sorted(['{:16}  {}'.format(k, str(v)) for k, v in new_status.items()],
                        key=lambda x: membership_key(x.split()), reverse=True)

    with open(get_bod_membership_file(semester=semester), 'w') as f:
        f.write('\n'.join(new_status) + '\n')
