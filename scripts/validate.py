"""Validate README references, image decoding, SVG safety and asset budgets."""
import re
import xml.etree.ElementTree as ET
from PIL import Image
from common import ROOT, ASSETS

def validate():
    content=(ROOT/'README.md').read_text(encoding='utf-8')
    assert not re.search(r'<(?:script|iframe|style|object|embed)\b',content,re.I), 'Active content in README'
    paths=set(re.findall(r'(?:src="|\]\()(assets/[^"\)]+)',content))
    assert paths, 'No image references'
    for relative in paths:
        assert (ROOT/relative).is_file(),f'Missing asset: {relative}'
    assert content.count('<!-- ACTIVITY:START -->')==1 and content.count('<!-- ACTIVITY:END -->')==1
    for src in ASSETS.glob('*.svg'):
        tree=ET.parse(src)
        assert tree.getroot().tag.endswith('svg')
        for node in tree.iter():
            assert node.tag.split('}')[-1] not in ['script','foreignObject','image'],f'Unsafe SVG: {src.name}'
            assert not any(k.lower().startswith('on') for k in node.attrib),f'SVG handler: {src.name}'
    total=0
    for src in sorted(ASSETS.glob('*.gif')):
        size=src.stat().st_size
        assert size<3_000_000,f'GIF exceeds 3 MB: {src.name}'
        total+=size
        with Image.open(src) as im:
            assert im.n_frames>1 and im.info.get('loop')==0,f'Not a looping animation: {src.name}'
            duration=0
            for index in range(im.n_frames):
                im.seek(index)
                im.load()
                duration+=im.info.get('duration',0)
            assert duration>1000
            print(f'{src.name}: {im.n_frames} frames / {duration/1000:.1f}s / {size/1024:.0f} KiB')
    assert total<6_000_000,'Combined animation budget exceeds 6 MB'
    for src in ASSETS.glob('*.png'):
        with Image.open(src) as im:
            im.verify()
    print(f'Validated {len(paths)} README assets, SVG safety, PNG decoding and GIF frames.')

if __name__=='__main__':
    validate()
