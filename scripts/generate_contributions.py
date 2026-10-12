"""Render actual calendar counts with a scanning overlay; no synthetic activity."""
from PIL import ImageDraw
from common import ASSETS, GREEN, CYAN, MUTED, canvas, font, save_gif, svg, text

LEVELS={'NONE':'#142332','FIRST_QUARTILE':'#174632','SECOND_QUARTILE':'#27784e','THIRD_QUARTILE':'#42b875','FOURTH_QUARTILE':GREEN}

def generate(data=None,state='CONFIGURATION REQUIRED'):
    calendar=data.get('calendar') if data else None
    base=canvas(1000,260,'contributions.scan  /  public GitHub calendar')
    d=ImageDraw.Draw(base)
    body=text(30,35,'CONTRIBUTIONS / PUBLIC GITHUB CALENDAR',14,CYAN)
    if calendar:
        weeks=calendar['weeks']
        d.text((30,65),f"{calendar['totalContributions']} contributions / rolling year",font=font(16),fill=GREEN)
        body+=text(30,80,f"{calendar['totalContributions']} contributions / rolling year",16,GREEN)
        last_month=None
        for col,week in enumerate(weeks):
            month=week['contributionDays'][0]['date'][5:7]
            if month!=last_month and col<51:
                import calendar as cal
                label=cal.month_abbr[int(month)]
                d.text((46+col*17,95),label,font=font(10),fill=MUTED)
                body+=text(46+col*17,105,label,10,MUTED)
                last_month=month
            for day in week['contributionDays']:
                x,y=46+col*17,116+day['weekday']*15
                color=LEVELS[day['contributionLevel']]
                d.rounded_rectangle((x,y,x+12,y+10),radius=2,fill=color)
                body+=f'<rect x="{x}" y="{y}" width="12" height="10" rx="2" fill="{color}"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>'
        caption=f"{state} / {data.get('calendar_fetched_at',data['fetched_at'])}"
    else:
        d.text((30,85),'AWAITING VERIFIED CONTRIBUTION DATA',font=font(21),fill=GREEN)
        message=data['calendar_status'] if data else 'Connect your username in profile.json, then run the update workflow.'
        d.text((30,130),message,font=font(14),fill=MUTED)
        body+=text(30,100,'AWAITING VERIFIED CONTRIBUTION DATA',21,GREEN)+text(30,145,message,14,MUTED)
        caption=state+' / no contribution counts displayed'
    d.text((30,235),caption,font=font(12),fill=MUTED)
    body+=text(30,248,caption,12,MUTED)
    base.save(ASSETS/'contribution-static.png')
    (ASSETS/'contribution-static.svg').write_text(svg(1000,260,body,'GitHub contribution calendar'),encoding='utf-8')
    frames=[]
    for i in range(48):
        im=base.copy()
        overlay=ImageDraw.Draw(im)
        x=30+round(i/47*938)
        # Thin moving scan at top/bottom; calendar values and brightness never change.
        overlay.line((x,55,x+18,55),fill=CYAN,width=2)
        overlay.line((x,226,x+18,226),fill=GREEN,width=2)
        frames.append(im)
    save_gif(frames,ASSETS/'contribution-animation.gif',[100]*47+[1200])
    animated=body+'<rect x="30" y="55" width="18" height="2" fill="#67dfee"><animate attributeName="x" values="30;968;30" dur="8s" repeatCount="indefinite"/></rect>'
    (ASSETS/'contribution-animation.svg').write_text(svg(1000,260,animated,'Contribution calendar with scanning accent'),encoding='utf-8')
