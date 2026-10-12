"""Build local banner and skill cards; all text remains readable without animation."""
from common import ASSETS, GREEN, CYAN, MUTED, svg, text

SKILLS={
 'languages':('Languages',['Python','Java','C#','TypeScript','JavaScript','SQL']),
 'backend':('Backend',['ASP.NET Core','Flask','REST APIs']),
 'frontend':('Frontend',['React','HTML','CSS']),
 'databases':('Databases',['PostgreSQL','SQLite','Supabase']),
 'security':('Cloud & Security',['AWS Cloud Security','Linux','IAM','Network Security']),
 'automation':('AI & Automation',['LLM Integration','AI Agents','Python Automation'])
}

def generate():
    body=text(36,39,'MW / ENGINEERING & SECURITY',13,CYAN)
    body+=text(36,95,'Mohamed Waleed',42)+text(36,133,'Backend systems. Cloud security. Applied AI.',18,MUTED)
    body+=text(36,177,'SOFTWARE DEVELOPER  /  CYBERSECURITY ENTHUSIAST',12,GREEN)
    body+='<path d="M795 38 L925 38 L925 153 L860 185 L795 153 Z" fill="#0e241e" stroke="#75f7ac" stroke-width="2"/><path d="M827 100 L850 120 L893 72" fill="none" stroke="#67dfee" stroke-width="4"/>'
    (ASSETS/'cyber-banner.svg').write_text(svg(1000,212,body,'Mohamed Waleed — backend, cloud security and applied AI'),encoding='utf-8')
    for key,(title,skills) in SKILLS.items():
        body=text(24,34,title.upper(),18,CYAN)
        x,y=24,58
        for skill in skills:
            w=len(skill)*10+22
            if x+w>468:
                x,y=24,y+34
            body+=f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="5" fill="#122335" stroke="#2a4053"/>'+text(x+11,y+20,skill,16,GREEN)
            x+=w+8
        (ASSETS/f'skills-{key}.svg').write_text(svg(490,138,body,title+': '+', '.join(skills)),encoding='utf-8')

if __name__=='__main__':
    generate()
