import bs4
import requests


class Team:
    def __init__(self, rank, name, played, won, drawn, lost, bye, gf, ga, pts):
            self.rank = rank
            self.name = name
            self.played = played
            self.won = won
            self.drawn = drawn
            self.lost = lost
            self.bye = bye
            self.gf = gf
            self.ga = ga
            self.diff = str(int(gf)-int(ga))
            self.pts = pts

    def __str__(self):
        str_format = '{:>3} {:<12} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>3} {:>2}'
        return str_format.format(self.rank, self.name, self.played, self.won,
                                 self.drawn, self.lost, self.bye, self.gf,
                                 self.ga, self.diff, self.pts)


class Ladder:
    def __init__(self, ladder):
        self.ladder = [l for l in ladder]

    def __iter__(self):
        yield from self.ladder

    def __str__(self):
        str_format = '{:>19} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>3} {:>2}'
        header = str_format.format('P','W','D','L','B','F','A','+/-','pts')
        return header + '\n' + '\n'.join(str(team) for team in self.ladder)


def generate_ladder():
    data = requests.get('http://www.nrl.com/telstrapremiership/nrlladder/tabid/10251/default.aspx')
    soup = bs4.BeautifulSoup(data.text, 'html.parser')
    ladder = soup.find('table',{'id':'LadderGrid'})('tbody')[0]

    for l in ladder.findAll('tr'):
        (rank, club, played, won, drawn, 
        lost, bye, gf, ga, 
        _, _ , _, pts, _, _) = (c.get_text() for c in l.findChildren())
        
        team = Team(rank, club, played, won, drawn, lost, bye, gf, ga, pts)

        yield team


ladder = Ladder(generate_ladder())

print(ladder)

