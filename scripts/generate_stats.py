"""Fetch only public GitHub data; retain an explicitly dated snapshot on failure."""
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone, timedelta, date
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from common import ROOT, ASSETS, config, svg, text, GREEN, CYAN, MUTED
from public_calendar import fetch_calendar

SNAPSHOT = ASSETS/'github-data.json'
USERNAME = re.compile(r'^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$')

def request(path, token='', payload=None):
    headers={'Accept':'application/vnd.github+json','User-Agent':'mohamed-profile-generator','X-GitHub-Api-Version':'2022-11-28'}
    if token:
        headers['Authorization']='Bearer '+token
    data=json.dumps(payload).encode() if payload else None
    if data:
        headers['Content-Type']='application/json'
    for attempt in range(3):
        try:
            with urlopen(Request('https://api.github.com'+path,data=data,headers=headers),timeout=25) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code not in [429,500,502,503,504] or attempt==2:
                # Do not emit raw response bodies, headers, or credentials.
                raise RuntimeError(f'GitHub API HTTP {exc.code}') from None
        except (URLError,TimeoutError):
            if attempt==2:
                raise RuntimeError('GitHub API connection unavailable') from None
        time.sleep(2**attempt)

def streaks(weeks, today=None):
    today=today or datetime.now(timezone.utc).date()
    days=sorted((d for w in weeks for d in w['contributionDays']),key=lambda d:d['date'])
    active={date.fromisoformat(d['date']) for d in days if d['contributionCount']>0 and date.fromisoformat(d['date'])<=today}
    longest=run=0
    previous=None
    for day in sorted(active):
        run=run+1 if previous and day-previous==timedelta(days=1) else 1
        longest=max(longest,run)
        previous=day
    cursor=today if today in active else today-timedelta(days=1)
    current=0
    while cursor in active:
        current+=1
        cursor-=timedelta(days=1)
    return current,longest

def fetch(username, token):
    user=request('/users/'+username,token)
    repos=[]
    page=1
    while True:
        batch=request(f'/users/{username}/repos?type=owner&per_page=100&page={page}',token)
        repos.extend(r for r in batch if not r.get('private'))
        if len(batch)<100:
            break
        page+=1
    # Public, owned, non-fork repositories. Byte counts from GitHub Linguist.
    languages=Counter()
    for repo in repos:
        if not repo['fork']:
            languages.update(request('/repos/'+repo['full_name']+'/languages',token))
    events=request(f'/users/{username}/events/public?per_page=30',token)
    activity=[{'type':e['type'],'repo':e['repo']['name'],'date':e['created_at'][:10]} for e in events[:5]]
    calendar=None
    calendar_status='Contribution calendar requires a GitHub token.'
    if token:
        query='query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}'
        try:
            result=request('/graphql',token,{'query':query,'variables':{'login':username}})
            if result.get('errors') or not result.get('data',{}).get('user'):
                raise RuntimeError('Contribution calendar unavailable')
            calendar=result['data']['user']['contributionsCollection']['contributionCalendar']
            calendar_status='GitHub contribution calendar / rolling year'
        except (RuntimeError,KeyError,TypeError):
            calendar_status='Contribution API unavailable; counts are not estimated.'
    if calendar is None:
        try:
            calendar=fetch_calendar(username)
            calendar_status='Verified public GitHub calendar / rolling year'
        except (URLError,TimeoutError,ValueError,KeyError,UnicodeError):
            calendar_status='Contribution calendar unavailable; counts are not estimated.'
    return {'username':user['login'],'fetched_at':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
            'public_repos':user['public_repos'],'stars':sum(r['stargazers_count'] for r in repos),
            'languages':dict(languages.most_common(6)),'activity':activity,
            'calendar':calendar,'calendar_status':calendar_status}

def render(data, state):
    body=text(30,35,'03 / GITHUB TELEMETRY',15,CYAN)
    labels=['PUBLIC REPOS','STARS RECEIVED','CONTRIBUTIONS / YEAR','CURRENT STREAK / DAYS']
    values=['—']*4
    if data:
        values[:2]=[data['public_repos'],data['stars']]
        if data.get('calendar'):
            values[2]=data['calendar']['totalContributions']
            values[3]=streaks(data['calendar']['weeks'],date.fromisoformat(data['fetched_at'][:10]))[0]
    for i,(label,value) in enumerate(zip(labels,values)):
        x=30+i*242
        body+=text(x,82,value,32,GREEN)+text(x,110,label,11,MUTED)
    body+=text(30,153,'LANGUAGES / top six by public non-fork code bytes',14,CYAN)
    languages=data.get('languages',{}) if data else {}
    total=sum(languages.values())
    x=30
    if total:
        for i,(name,count) in enumerate(languages.items()):
            width=940*count/total
            color=[GREEN,CYAN,'#bcafff','#e9c16b','#ed7180','#76a8ed'][i]
            body+=f'<rect x="{x:.2f}" y="170" width="{width:.2f}" height="8" fill="{color}"/>'
            x+=width
            body+=text(30+(i%3)*310,205+(i//3)*25,f'{name[:22]} {count/total:.1%}',13,color)
    else:
        body+=text(30,200,'Language data not available yet.',14,MUTED)
    stamp=data['fetched_at'] if data else 'not fetched'
    body+=text(30,268,f'{state}  /  last successful fetch: {stamp}',12,MUTED)
    (ASSETS/'stats.svg').write_text(svg(1000,290,body,'GitHub statistics, sourced from the public GitHub API'),encoding='utf-8')
    # Escape Markdown via restricting event names, dates and repository identifiers.
    lines=[]
    if data:
        for event in data['activity']:
            repo=event['repo']
            if re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):
                kind={'PushEvent':'Pushed code','CreateEvent':'Created a branch or repository','PullRequestEvent':'Pull request activity','IssuesEvent':'Issue activity','WatchEvent':'Starred a repository','ForkEvent':'Forked a repository','ReleaseEvent':'Release activity'}.get(event['type'],'Public activity')
                lines.append(f"- {event['date']} · {kind} in [{repo}](https://github.com/{repo})")
    block='\n'.join(lines) or 'Public activity will appear after the first successful GitHub API refresh.'
    if data:
        if not lines:
            block='No recent public events were returned by GitHub.'
        block+=f"\n\n*Snapshot: {stamp}. Public events only; GitHub may delay or omit events.*"
    readme=ROOT/'README.md'
    if readme.exists():
        content=readme.read_text(encoding='utf-8')
        content=re.sub(r'(?s)(<!-- ACTIVITY:START -->).*?(<!-- ACTIVITY:END -->)',lambda m:m[1]+'\n\n'+block+'\n\n'+m[2],content)
        readme.write_text(content,encoding='utf-8')

def generate(offline=False):
    username=os.getenv('PROFILE_USERNAME') or config()['username']
    if username=='YOUR_GITHUB_USERNAME':
        # In username/username profile repos the owner is a safe automatic default.
        repository=os.getenv('GITHUB_REPOSITORY','')
        parts=repository.split('/')
        if len(parts)==2 and parts[0].lower()==parts[1].lower():
            username=parts[0]
    data=None
    if SNAPSHOT.exists():
        saved=json.loads(SNAPSHOT.read_text(encoding='utf-8'))
        if saved['username'].lower()==username.lower():
            data=saved
    state='CONFIGURATION REQUIRED'
    if username!='YOUR_GITHUB_USERNAME' and not USERNAME.fullmatch(username):
        raise ValueError('Invalid GitHub username')
    if username!='YOUR_GITHUB_USERNAME':
        if offline:
            state='OFFLINE / saved snapshot' if data else 'OFFLINE / no snapshot'
        else:
            try:
                data=fetch(username,os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN',''))
                SNAPSHOT.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
                state='API SYNC COMPLETE'
            except (RuntimeError,KeyError,TypeError,ValueError) as exc:
                print('::warning::GitHub refresh failed; retained the last successful snapshot.' if data else '::warning::GitHub refresh failed; showing unavailable data.')
                state='STALE / API unavailable' if data else 'API UNAVAILABLE / no snapshot'
    render(data,state)
    return data,state

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--offline',action='store_true')
    generate(p.parse_args().offline)
