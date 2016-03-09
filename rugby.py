import bs4
import requests
from threading import Thread
from functools import wraps


def threaded(func):
    def wrapped_func(ret_val, *args, **kwargs):
        """Calls the function and appends the return value to ret_val"""
        val = func(*args, **kwargs)
        ret_val.append(val)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Creates a new thread with wrapped_func, adds an empty list to the
           thread for return value. Return a running thread"""
        ret_val = []
        thread = Thread(target=wrapped_func, args=(ret_val,)+args, kwargs=kwargs)
        thread.ret_val = ret_val
        thread.start()
        return thread

    return wrapper


class Team:
    def __init__(self, rank, name, played, won, drawn, lost, gf, ga, pts, longest):
            self.rank = rank
            self.name = name
            self.played = played
            self.won = won
            self.drawn = drawn
            self.lost = lost
            self.gf = gf
            self.ga = ga
            self.diff = str(int(gf)-int(ga))
            self.pts = pts
            self.longest = longest # longest team name

    def __str__(self):
        str_format = '{:>3} {:<%s} {:>2} {:>2} {:>2} {:>2} {:>3} {:>3} {:>3} {:>2}' % (self.longest)
        return str_format.format(self.rank, self.name, self.played, self.won,
                                 self.drawn, self.lost, self.gf,
                                 self.ga, self.diff, self.pts)


class Ladder:
    def __init__(self, league, ladder, offset):
        self.league = league
        self.ladder = [l for l in ladder]
        self.offset = offset

    def __iter__(self):
        yield from self.ladder

    def __str__(self):
        str_format = '{:>%s} {:>2} {:>2} {:>2} {:>3} {:>3} {:>3} {:>2}\n' % (self.offset)
        header = str_format.format('P','W','D','L','F','A','+/-','pts')
        return self.league +'\n' +\
               header +\
               '\n'.join(str(team) for team in self.ladder)


def nrl_selector(attrs):
    (rank, club, played, won, drawn, 
    lost, _, gf, ga, 
    _, _ , _, pts, _, _) = (attr.get_text() for attr in attrs)
        
    team = Team(rank, club, played, won, drawn, lost, gf, ga, pts, 12)
    return team


def super_league_selector(attrs):
    rank,_,_,club,played,won,lost,drawn,gf,ga,_,pts = (attr.get_text() for attr in attrs)
    team = Team(rank+'.',club,played,won,drawn,lost,gf,ga,pts, 20)
    return team



@threaded
def generate_ladder(url, tag, attr, league):
    data = requests.get(url)
    soup = bs4.BeautifulSoup(data.text, 'html.parser')
    ladder = soup.find(tag,attr)('tbody')[0]('tr')
    teams = []
    for l in ladder:
        if league == 'nrl':
            team = nrl_selector(l.findChildren())
        else:
            team = super_league_selector(l.findChildren())
        teams.append(team)
    return teams


#ladder = Ladder(generate_ladder())
#
#print(ladder)
url = 'http://www.nrl.com/telstrapremiership/nrlladder/tabid/10251/default.aspx'
tag = 'table'
attr = {'id':'LadderGrid'}
nrl_ladder = generate_ladder(url, tag, attr, 'nrl')


url = 'http://www.rugby-league.com/superleague/tables'
tag = 'table'
attr = {'class':'table table-striped'}
super_league_ladder = generate_ladder(url,tag,attr,'super_league')

nrl_ladder.join()
super_league_ladder.join()

nrl_ladder = nrl_ladder.ret_val[0]
super_league_ladder = super_league_ladder.ret_val[0]

print(Ladder('NRL', nrl_ladder, '19'))
print('\n')
print(Ladder('Super League', super_league_ladder, '27'))






