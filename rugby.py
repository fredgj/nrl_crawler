import bs4
import requests
import asyncio


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
        self.ladder = ladder
        self.offset = offset

    def __iter__(self):
        yield from self.ladder

    def __str__(self):
        str_format = '{:>%s} {:>2} {:>2} {:>2} {:>3} {:>3} {:>3} {:>2}\n' % (self.offset)
        header = str_format.format('P','W','D','L','F','A','+/-','pts')
        teams = '\n'.join(str(team) for team in self.ladder)
        
        return '{}\n{}\n{}\n'.format(self.league,
                        header,
                        teams)


def nrl_selector(attrs):
    (rank, club, played, won, drawn, lost, _, 
    gf, ga, _, _ , _, pts, _, _) = (attr.get_text() for attr in attrs)
        
    team = Team(rank, club, played, won, drawn, lost, gf, ga, pts, 12)
    return team


def sl_selector(attrs):
    (rank, _, _, club, played, won, lost, drawn, 
    gf, ga, _, pts) = (attr.get_text() for attr in attrs)
    team = Team(rank+'.',club,played,won,drawn,lost,gf,ga,pts, 20)
    return team


async def fetch(url, league):
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None,requests.get, url)
    response = await future
    return response.text, league


def generate_ladder(data, attr, league):
    soup = bs4.BeautifulSoup(data, 'html.parser')
    ladder = soup.find('table', attr)('tbody')[0]('tr')
    selector = nrl_selector if league == 'NRL' else sl_selector
    for l in ladder:
        team = selector(l.findChildren())
        yield team


loop = asyncio.get_event_loop()

nrl = 'http://www.nrl.com/telstrapremiership/nrlladder/tabid/10251/default.aspx'
sl = 'http://www.rugby-league.com/superleague/tables'

tasks = (fetch(nrl, 'NRL'), fetch(sl, 'Super League'))
results = loop.run_until_complete(asyncio.gather(*tasks))


for data, league in results:
    if league == 'NRL':
        attr = {'id':'LadderGrid'}
        offset = 19
    else:
        attr = {'class':'table table-striped'}
        offset = 27
    
    ladder = (generate_ladder(data, attr, league))
    ladder = Ladder(league, ladder, offset)
    print(ladder)


