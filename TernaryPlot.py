import pdb
import pandas as pd
from pyrolite.plot import pyroplot
import matplotlib.pyplot as plt
import plotly.express as px
import os

plt.rc('figure', figsize = (15,12))
plt.rc('font', size = 28 )
plt.rc('axes', labelsize=24)


def load_briefsummary():
    if os.path.exists('ParsedBriefsummary.pkl'):
        BS = pd.read_pickle('ParsedBriefsummary.pkl')
    else:
        from BopFoxFeaturizer.brief_summary_parser import StructSummaryParser
        BS = StructSummaryParser().BriefSummary
        BS.to_pickle('ParsedBriefsummary.pkl')
    return BS

def get_frac_of_spec(THEBS, thespec):
    X = THEBS['atom_A'].str.contains(thespec)*THEBS['num_atom_A'] \
            +THEBS['atom_B'].str.contains(thespec)*THEBS['num_atom_B'] \
            +THEBS['atom_C'].str.contains(thespec)*THEBS['num_atom_C'] 
    return  (X/THEBS['num_atoms']).fillna(0)

def get_fractions_by_components(THEBS, thecomponents):
    for spec in thecomponents:
        THEBS[spec] = get_frac_of_spec(THEBS, spec)
    return THEBS[thecomponents]


def clean_briefsummary(THEBS):
    THEBS.rename(columns={'':'Phase'}, inplace=True)
    for toremove in [ 'bulk', '-.*','_.*', '\..*' ]:
        THEBS['Phase'] = THEBS['Phase'].str.replace(toremove,'', regex=True)
    for other in ['D0_19','D03', 'D0', 'B2','D32',  'L12', 'L10']:
        THEBS['Phase'] = THEBS['Phase'].str.replace(other,'hcp', regex=True)
    return THEBS

def ternary_matplotlib(THEBS, thecomponents):
    fig, ax = plt.subplots()
    for phase, group in THEBS.groupby(['Phase']):
        ax =group[thecomponents].pyroplot.scatter(
                label=phase, marker='o', ax=ax, s = 10*group['num_atoms'], alpha=0.5
                )
    for thisax in [ax.laxis, ax.raxis, ax.taxis ] :
        thisax.set_label_rotation_mode('horizontal')
        thisax.set_label_position('tick1')
    ax.tick_params(labelrotation='horizontal', labelsize=18)
    ax.grid('on')
    ax.set_title('samples for the Cr-Co-W system', y=-0.15)
    leg = ax.legend()
    # the markers at legend neeed to be fixed
    for lh in leg.legendHandles:
        lh.set_alpha(1)
        lh.set_sizes([50])
    fig.tight_layout()
    return fig

def ternary_plotly(THEBS, thecomponents):
    FIF = px.scatter_ternary(THEBS, 
            a=thecomponents[0],
            b=thecomponents[1], 
            c=thecomponents[2],
            color='Phase', size='num_atoms', 
            hover_name=THEBS.index, title = 'samples on the Cr-Co-W system')
    FIF.update_layout(
            font_size=20,
            title_pad_b = 100, # I couldnt make this to have effect
            title_y = 0.95
            )
    return FIF

if __name__ == '__main__':
    components = ['Co','Cr','W']
    BS = clean_briefsummary(load_briefsummary())
    BS[components] = get_fractions_by_components(BS, components)
# with matplotlib + pyrolite. quite dirty but I know all the options 
    mplfig = ternary_matplotlib(BS, components)
    mplfig.savefig('example_matplotlib.pdf')
# with plotly, very nice web images but cant contrlol all configs at the moment.
# will also need plotly-orca to save pdf.
    FIF = ternary_plotly(BS, components)
    FIF.write_image('example_plotly.pdf', width=900, height=700) 
# will open web visualization served @ localhosta
#FIF.show()
