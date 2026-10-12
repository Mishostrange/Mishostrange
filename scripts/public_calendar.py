"""Strict public-calendar fallback. Fail closed if GitHub's markup changes."""
import re
from html.parser import HTMLParser
from datetime import date, timedelta
from collections import defaultdict
from urllib.request import Request, urlopen

LEVELS=['NONE','FIRST_QUARTILE','SECOND_QUARTILE','THIRD_QUARTILE','FOURTH_QUARTILE']

class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells={}
        self.tooltips={}
        self.target=None
        self.buffer=[]
        self.heading=False
        self.heading_text=[]

    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='td' and 'ContributionCalendar-day' in a.get('class','').split() and a.get('data-date'):
            self.cells[a['id']]={'date':a['data-date'],'level':int(a['data-level'])}
        if tag=='tool-tip':
            self.target=a.get('for')
            self.buffer=[]
        if tag=='h2' and a.get('id')=='js-contribution-activity-description':
            self.heading=True

    def handle_data(self,data):
        if self.target:
            self.buffer.append(data)
        if self.heading:
            self.heading_text.append(data)

    def handle_endtag(self,tag):
        if tag=='tool-tip' and self.target:
            self.tooltips[self.target]=''.join(self.buffer).strip()
            self.target=None
        if tag=='h2':
            self.heading=False

def parse_calendar(html):
    p=CalendarParser()
    p.feed(html)
    if not 350<=len(p.cells)<=371:
        raise ValueError('Incomplete public contribution calendar')
    days=[]
    for identity,cell in p.cells.items():
        tip=p.tooltips.get(identity,'')
        match=re.match(r'^(No|[\d,]+) contributions? on ',tip)
        if not match or cell['level'] not in range(5):
            raise ValueError('Unrecognized calendar tooltip or level')
        count=0 if match[1]=='No' else int(match[1].replace(',',''))
        if (count==0)!=(cell['level']==0):
            raise ValueError('Inconsistent calendar count and color')
        day=date.fromisoformat(cell['date'])
        days.append({'date':day.isoformat(),'weekday':(day.weekday()+1)%7,
                     'contributionCount':count,'contributionLevel':LEVELS[cell['level']]})
    days.sort(key=lambda d:d['date'])
    first=date.fromisoformat(days[0]['date'])
    if any(date.fromisoformat(d['date'])!=first+timedelta(days=i) for i,d in enumerate(days)):
        raise ValueError('Non-contiguous public contribution calendar')
    header=' '.join(''.join(p.heading_text).split())
    total_match=re.fullmatch(r'([\d,]+) contributions? in the last year',header)
    total=sum(d['contributionCount'] for d in days)
    if not total_match or int(total_match[1].replace(',',''))!=total:
        raise ValueError('Calendar total does not match verified daily counts')
    origin=first-timedelta(days=(first.weekday()+1)%7)
    weeks=defaultdict(list)
    for day in days:
        weeks[(date.fromisoformat(day['date'])-origin).days//7].append(day)
    return {'totalContributions':total,'weeks':[{'contributionDays':weeks[i]} for i in sorted(weeks)]}

def fetch_calendar(username):
    req=Request(f'https://github.com/users/{username}/contributions',headers={'User-Agent':'mohamed-profile-generator','Accept-Language':'en-US'})
    with urlopen(req,timeout=25) as response:
        return parse_calendar(response.read(2_000_000).decode('utf-8'))
