"""Raster terminal typing animation plus a complete, static SVG fallback."""
from PIL import ImageDraw, Image, ImageChops, ImageFilter
from common import ASSETS, GREEN, CYAN, WHITE, MUTED, canvas, font, save_gif, svg, text

LINES = [
    ('┌──(mohamed㉿github)-[~]', CYAN), ('└─$ whoami', GREEN), ('', WHITE),
    ('> Mohamed Waleed', WHITE), ('> Software Developer', WHITE),
    ('> Cybersecurity Enthusiast', WHITE), ('', WHITE),
    ('└─$ ./initialize_profile.sh', GREEN), ('', WHITE),
    ('[+] Initializing environment...', MUTED),
    ('[+] Loading development skills...', MUTED),
    ('[+] Loading security modules...', MUTED),
    ('[+] Connecting to GitHub...', MUTED), ('[+] Access granted.', GREEN),
    ('', WHITE), ('Welcome to my digital workspace.', CYAN)
]

def generate():
    frames, durations = [], []
    base = canvas(1000, 566, 'mohamed@github  /  profile.init')
    def glow(im):
        light=ImageChops.subtract(im,Image.new('RGB',im.size,'#203040')).filter(ImageFilter.GaussianBlur(3))
        light=light.point(lambda v:round(v*.13))
        return ImageChops.add(im,light)
    # Symbols missing from the redistributable font are drawn as paths.
    def draw_line(d, xy, value, color):
        x,y = xy
        for char in value:
            if char == '㉿':
                d.ellipse((x+1,y+5,x+11,y+15), outline=color)
                d.line((x+6,y+2,x+6,y+18), fill=color)
            elif char in '┌└─':
                d.line((x,y+11,x+12,y+11), fill=color)
                if char != '─':
                    d.line((x+2,y+(11 if char=='┌' else 2),x+2,y+(20 if char=='┌' else 11)),fill=color)
            else:
                d.text((x,y),char,font=font(20),fill=color)
            x += 12
    for row, (line, color) in enumerate(LINES):
        if not line:
            continue
        # Commands and identity type; progress messages appear one after another.
        stops = list(range(0, len(line), 3)) + [len(line)] if row in [0,1,3,4,5,7,15] else [len(line)]
        for n in stops:
            im = base.copy()
            d = ImageDraw.Draw(im)
            for prev in range(row):
                draw_line(d,(34,66+prev*29),LINES[prev][0],LINES[prev][1])
            draw_line(d,(34,66+row*29),line[:n],color)
            cx = 34+n*12
            d.rectangle((cx+2,70+row*29,cx+11,88+row*29),fill=GREEN)
            frames.append(glow(im))
            durations.append(70 if n<len(line) else (260 if row<9 else 380))
    final = frames[-1].copy()
    d=ImageDraw.Draw(final)
    d.rectangle((34+len(LINES[-1][0])*12,70+15*29,46+len(LINES[-1][0])*12,88+15*29),fill='#070d16')
    for _ in range(3):
        frames.extend([final, frames[-1]])
        durations.extend([500,500])
    save_gif(frames, ASSETS/'terminal.gif', durations)
    final.save(ASSETS/'terminal-static.png')
    body = text(34,34,'mohamed@github / profile.init',14,MUTED)
    body += ''.join(text(34,85+i*29,line,20,color) for i,(line,color) in enumerate(LINES))
    (ASSETS/'terminal.svg').write_text(svg(1000,566,body,'Mohamed Waleed: terminal introduction'),encoding='utf-8')

if __name__ == '__main__':
    generate()
