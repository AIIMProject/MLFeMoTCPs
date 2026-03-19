from ase.atoms import Atoms
from plotly import  graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import pdb

def plotly_atoms(
        theatoms: Atoms
        ):
    positions = theatoms.positions

    fig = go.Figure() # px.scatter_3d(
#            )
    fig.update_layout(
            margin={
                "t":5,
                "b":5,
                'l':5,
                'r': 0.5
                }
            )
    orig = np.array([0,0,0])


    get_cell_traces(fig, theatoms.cell.cellpar())

    for symb in theatoms.symbols.species():
        thisatoms : Atoms = Atoms( [ a for a in theatoms if a.symbol == symb ], cell = theatoms.cell )
        hovertext = [symb+f'{i}' for i, a in enumerate(thisatoms)]
        fig.add_traces(
                data = go.Scatter3d( 
                                    name = symb,
                                    x = thisatoms.positions[:,0],
                                    y = thisatoms.positions[:,1],
                                    z = thisatoms.positions[:,2], 
                                    hovertext= hovertext,  
                                    mode='markers',
                                    # opacity=0.7,
                                    marker={'line':{'color':'black','width':1}}
                                    ),
                )

    fig.update_scenes(
            {
                'xaxis_showgrid':False,
                'yaxis_showgrid':False,
                'zaxis_showgrid':False,
                'xaxis_showbackground': False,
                'yaxis_showbackground': False,
                'zaxis_showbackground': False,
                'aspectmode':'data',
                'camera_projection': {'type': 'orthographic' }}
            )

    fig.update_layout(legend={'yanchor': 'top','y': 0.9, 'xanchor': 'left', 'x':0.05 }, height=600, width=600)


    return fig

def get_cell_traces(thefig: go.Figure, cellpars: np.ndarray) -> None:

    a, b, c  = cellpars[:3]
    #b = cellpars[1]
    #c = cellpars[2]

    veca = pd.DataFrame.from_dict(
            {'x': [0, a],
             'y': [0,0],
             'z': [0,0],
             }
            )
    vecb = pd.DataFrame.from_dict(
            {'x': [0, 0],
             'y': [0,b],
             'z': [0,0],
             }
            )
    vecz = pd.DataFrame.from_dict(
            {'x': [0, 0],
             'y': [0,0],
             'z': [0,c],
             }
            )
    vecab = pd.DataFrame.from_dict(
            {'x': [a,a],
             'y': [0,b],
             'z': [0,0],
             }
            )
    vecba = pd.DataFrame.from_dict(
            {'x': [0,a],
             'y': [b,b],
             'z': [0,0],
             }
            )
    vecabc = pd.DataFrame.from_dict(
            {'x': [a,a],
             'y': [b,b],
             'z': [0,c],
             }
            )
    vecac = pd.DataFrame.from_dict(
            {'x': [a,a],
             'y': [0,0],
             'z': [0,c],
             }
            )
    vecbc = pd.DataFrame.from_dict(
            {'x': [0,0],
             'y': [b,b],
             'z': [0,c],
             }
            )
    vecca = pd.DataFrame.from_dict(
            {'x': [0,a,],
             'y': [0,0,],
             'z': [c,c,],
             }
            )
    veccb = pd.DataFrame.from_dict(
            {'x': [0,0,],
             'y': [0,b,],
             'z': [c,c,],
             }
            )
    veccba = pd.DataFrame.from_dict(
            {'x': [0,a,],
             'y': [b,b,],
             'z': [c,c,],
             }
            )
    veccab = pd.DataFrame.from_dict(
            {'x': [a,a,],
             'y': [0,b,],
             'z': [c,c,],
             }
            )

    box_line_opions ={'width': 1, 'color': 'black'}
    box_marker_options = { 'size' : 0.01 }


    thefig.add_traces(
            data = [
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=veca.x  , y=veca.y , z=veca.z   , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=vecb.x  , y=vecb.y , z=vecb.z   , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=vecz.x  , y=vecz.y , z=vecz.z   , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=vecab.x , y=vecab.y, z=vecab.z  , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=vecba.x , y=vecba.y, z=vecba.z  , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=vecabc.x, y=vecabc.y, z=vecabc.z, line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=vecac.x , y=vecac.y , z=vecac.z , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=vecbc.x , y=vecbc.y , z=vecbc.z , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=vecca.x , y=vecca.y , z=vecca.z , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=veccb.x , y=veccb.y , z=veccb.z , line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=False,legendgroup = 'cell', x=veccba.x, y=veccba.y, z=veccba.z, line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                go.Scatter3d(showlegend=True ,legendgroup = 'cell', x=veccab.x, y=veccab.y, z=veccab.z, line=box_line_opions, marker=box_marker_options, hoverinfo='skip', name = 'cell'),
                ]
                )

    thefig.update_scenes(xaxis = {'range' : [-a/10, a*1.1]}, yaxis = {'range': [-b/10, b*1.1]}, zaxis = {'range' : [-c/10, c*1.1]})

