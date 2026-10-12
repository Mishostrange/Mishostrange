"""One command rebuild. Use --offline for a reproducible local preview."""
import argparse
from common import ROOT, ASSETS, config
from generate_assets import generate as assets
from generate_ascii import generate as ascii_animation, create_source
from generate_terminal import generate as terminal
from generate_stats import generate as stats
from generate_contributions import generate as contributions

def build(offline=False):
    ASSETS.mkdir(exist_ok=True)
    assets()
    terminal()
    c=config()['ascii']
    source=ROOT/c['source']
    if not source.exists() and c['source']=='assets/cyber-source.png':
        create_source(source)
    ascii_animation(source=source,**{k:c[k] for k in ['columns','frames','fps','seed']})
    data,state=stats(offline)
    contributions(data,state)
    print('Profile assets generated successfully.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--offline',action='store_true')
    build(p.parse_args().offline)
