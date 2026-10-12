"""Configurable image -> luminance ASCII -> matrix reveal GIF/WebP pipeline."""
import argparse
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from common import ROOT, ASSETS, GREEN, CYAN, MUTED, canvas, font, config, save_gif

RAMP = ' .,:;i1tfLCG08@'

def create_source(path):
    """Original geometric cyber sentinel; fictional illustration, never a personal likeness."""
    im = Image.new('L',(640,440),0)
    d = ImageDraw.Draw(im)
    d.polygon([(90,432),(142,323),(210,286),(186,216),(203,117),(259,52),(320,29),(381,52),(437,117),(454,216),(430,286),(498,323),(550,432)],fill=130)
    d.polygon([(210,287),(216,140),(266,83),(320,55),(374,83),(424,140),(430,287),(373,329),(320,353),(267,329)],fill=38)
    d.polygon([(246,159),(280,122),(360,122),(394,159),(391,248),(351,291),(289,291),(249,248)],fill=190)
    d.polygon([(243,171),(397,171),(386,205),(254,205)],fill=20)
    d.line([(258,184),(292,190),(309,183)],fill=255,width=10)
    d.line([(331,183),(348,190),(382,184)],fill=255,width=10)
    d.polygon([(269,233),(371,233),(351,267),(289,267)],fill=70)
    d.line([(279,246),(361,246)],fill=210,width=4)
    d.line([(150,413),(213,329),(266,361),(320,385),(374,361),(427,329),(490,413)],fill=220,width=6)
    d.line([(320,385),(320,435)],fill=235,width=4)
    im.save(path)

def generate(source=None, columns=92, frames=54, fps=12, seed=42, output=None):
    if not 20 <= columns <= 160 or not 12 <= frames <= 120 or not 4 <= fps <= 30:
        raise ValueError('Use 20..160 columns, 12..120 frames, and 4..30 fps')
    source = Path(source or ASSETS/'cyber-source.png')
    if not source.exists():
        raise FileNotFoundError(source)
    im = ImageOps.exif_transpose(Image.open(source)).convert('L')
    cell_w, cell_h = 8, 15
    rows = max(1,round(columns*im.height/im.width*cell_w/cell_h))
    if rows > 90:
        raise ValueError('Source aspect ratio too tall; crop the source before rendering')
    pixels = list(im.resize((columns,rows),Image.Resampling.LANCZOS).getdata())
    rng = random.Random(seed)
    reveal = [rng.random()*.32 + (i//columns)/rows*.58 for i in range(len(pixels))]
    width, height = max(640,columns*cell_w+48), rows*cell_h+104
    output = Path(output or ASSETS/'ascii-portrait.gif')
    if output.suffix.lower() not in ['.gif','.webp']:
        raise ValueError('Output must be .gif or .webp')
    result=[]
    for step in range(frames):
        progress = step/(frames-1)
        frame = canvas(width,height,'sentinel.ascii  /  character reconstruction')
        d = ImageDraw.Draw(frame)
        for i, value in enumerate(pixels):
            col,row = i%columns,i//columns
            char = RAMP[min(len(RAMP)-1,value*(len(RAMP)-1)//255)]
            if progress < reveal[i]:
                # Low density falling code before lock-in.
                char = rng.choice('01:/<>') if rng.random()<.075 else ' '
                color = '#234c42'
            else:
                color = CYAN if value>210 or (col+row)%13==0 else GREEN
                if progress < reveal[i]+.09:
                    char = rng.choice('01@%#')
                    color = '#e2edf4'
            if char != ' ':
                d.text((24+col*cell_w,62+row*cell_h),char,font=font(13),fill=color)
        d.text((24,height-28),'FICTIONAL CYBER ILLUSTRATION  /  not a personal portrait',font=font(12),fill=MUTED)
        result.append(frame)
    durations=[round(1000/fps)]*frames
    durations[-1]=2400
    if output.suffix.lower()=='.webp':
        result[0].save(output,save_all=True,append_images=result[1:],duration=durations,loop=0,quality=80,method=6)
    else:
        save_gif(result,output,durations)
    result[-1].save(output.with_name(output.stem+'-static.png'))

if __name__=='__main__':
    c=config()['ascii']
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT/c['source'])
    p.add_argument('--output',type=Path,default=ASSETS/'ascii-portrait.gif')
    for name in ['columns','frames','fps','seed']:
        p.add_argument('--'+name,type=int,default=c[name])
    a=p.parse_args()
    generate(**vars(a))
