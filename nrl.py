import bs4
import requests

data = requests.get('http://www.nrl.com/telstrapremiership/nrlladder/tabid/10251/default.aspx')

soup = bs4.BeautifulSoup(data.text, 'html.parser')

ladder = soup.find('table',{'id':'LadderGrid'})('tbody')

for l in ladder[0].findAll('tr'):
    rank, club, played, won, drawn, lost, bye, goals_f, goals_a, difference, _,_, pts,_,_ = l.findChildren()
    rank = rank.get_text()
    club = club.get_text()
    played = played.get_text()
    won = won.get_text()
    drawn = drawn.get_text()
    lost = lost.get_text()
    bye = bye.get_text()
    goals_f = goals_f.get_text()
    goals_a = goals_a.get_text()
    difference = difference.get_text()
    pts = pts.get_text()
    print(rank, club, played, won, drawn, lost, bye, goals_f, goals_a, difference, pts)


