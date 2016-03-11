import bs4
import requests
import asyncio


class Structure:
    _fields = []
    def __init__(self, *args):
        if len(args) != len(self._fields):
            raise TypeError('Expected {} args but were given {}').format(len(self._fields),
                                                                         len(args)) 
        for name, val in zip(self._fields, args):
            setattr(self, name, val)


class Team(Structure):
    _fields = ['rank','name','played','won',
               'drawn','lost','gf','ga','diff',
               'pts','longest']

    def __str__(self):
        str_format = '{:>3} {:<%s} {:>2} {:>2} {:>2} {:>2} {:>3} {:>3} {:>3} {:>2}' % (self.longest)
        return str_format.format(self.rank, self.name, self.played, self.won,
                                 self.drawn, self.lost, self.gf,
                                 self.ga, self.diff, self.pts)


class Ladder(Structure):
    _fields = ['league','ladder','offset']

    def __iter__(self):
        yield from self.ladder

    def __str__(self):
        str_format = '{:>%s} {:>2} {:>2} {:>2} {:>3} {:>3} {:>3} {:>2}' % (self.offset)
        header = str_format.format('P','W','D','L','F','A','+/-','pts')
        teams = '\n'.join(str(team) for team in self.ladder)
        
        return '{}\n{}\n{}\n'.format(self.league,
                        header,
                        teams)

    
async def fetch(url, league, what):
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None,requests.get, url)
    response = await future
    return response.text, league, what


def nrl_selector(attrs):
    (rank, club, played, won, drawn, lost, _, 
    gf, ga, diff, _ , _, pts, *rest) = (attr.get_text() for attr in attrs)
        
    team = Team(rank, club, played, won, drawn, lost, gf, ga, diff,pts, 12)
    return team


def sl_selector(attrs):
    (rank, _, _, club, played, won, lost, drawn, 
    gf, ga, diff, pts) = (attr.get_text() for attr in attrs)
    team = Team(rank+'.',club,played,won,drawn,lost,gf,ga,diff,pts, 20)
    return team


def generate_ladder(data, attr, league):
    soup = bs4.BeautifulSoup(data, 'html.parser')
    ladder = soup.find('table', attr)('tbody')[0]('tr')
    selector = nrl_selector if league == 'NRL' else sl_selector
    for l in ladder:
        team = selector(l.findChildren())
        yield team


def format_match_data(home_team, away_team):
    _,_,team1,_,_,points1,*rest = home_team
    team2,_,_,points2,*rest = away_team
    team1 = team1.get_text()
    team2 = team2.get_text()
    points1 = points1.get_text()
    points2 = points2.get_text()
    points1 = points1 if int(points1) >= 10 else ' '+points1
    points2 = points2 if int(points2) >= 10 else ' '+points2
    if len(team1) < len(team2):
        team1 += ' '*(len(team2)-len(team1))
    else:
        team2 += ' '*(len(team1)-len(team2))
    res_format = '{} {}\n{} {}\n' % ()
    return res_format.format(team1,points1,team2,points2)


def get_score(data):
    for match in reversed(data):
        match = iter(match) 
        for team in match:
            away_team = next(match) 
            yield format_match_data(team, away_team)


def get_all_scores(data):
    soup = bs4.BeautifulSoup(data, 'html.parser')
    dates = soup.find_all('div',class_='ncet')
    matches = soup.find_all('div', class_='compgrp')
    games = [game for game in zip(dates,matches)]
    for d, m in reversed(games):
        round_, date = d.children
        yield '{} {}'.format(round_.get_text(), date.get_text())
        yield from get_score(m('tbody'))



loop = asyncio.get_event_loop()

nrl = 'http://www.nrl.com/telstrapremiership/nrlladder/tabid/10251/default.aspx'
sl = 'http://www.rugby-league.com/superleague/tables'
scores_nrl = 'http://www.scorespro.com/rugby-league/ajaxdata.php?country=australia&comp=nrl&league=regular-season&season=2016&status=results&page=1'
scores_sl = 'http://www.scorespro.com/rugby-league/ajaxdata.php?country=europe&comp=super-league&league=&season=2016&status=results&page=1'



tasks = (fetch(nrl, 'NRL', 'ladder'), 
         fetch(sl, 'Super League', 'ladder'), 
         fetch(scores_nrl,'NRL', 'scores'), 
         fetch(scores_sl, 'Super League', 'scores'))

results = loop.run_until_complete(asyncio.gather(*tasks))


for data, league, what in results:
    if what == 'ladder':
        if league == 'NRL':
            attr = {'id':'LadderGrid'}
            offset = 19
        else:
            attr = {'class':'table table-striped'}
            offset = 27
    
        ladder = (generate_ladder(data, attr, league))
        ladder = Ladder(league, ladder, offset)
        print(ladder)
    elif what == 'scores':
        print(league)
        for score in get_all_scores(data):
            print(score)



