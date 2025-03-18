import osmnx as ox
import networkx as nx
import folium
from flask import Flask, render_template, request

app = Flask(__name__)

# Define building coordinates including the additional buildings
buildings = {
    "Oastler Building": (53.644687676943896, -1.777221326180791),
    "Charles Sikes Building": (53.64321393954174, -1.7761258832958444),
    "Spärck Jones Building": (53.64121612620168, -1.7785260024007055),
    "Richard Steinitz Building": (53.64424613216057, -1.7778734022227625),
    "Harold Wilson Building": (53.643507343894264, -1.7783422122519073),
    "Haslett Building": (53.641657771293445, -1.7776854868933023),
    "Barbara Hepworth Building": (53.64166710212857, -1.77920305167703),
    "Laura Annie Wilson Building": (53.6431033847188, -1.7776944711201437),
}

# Template for the popups
building_info = {
    "Oastler Building": "<h1>Oastler Building</h1>"
                        "<img src='static/images/Oastlerbuilding.jpg' width=400px>"
                        "<p>The home of Music, Humanities and Media. History, English"
                        "Language, Linguistics and Modern Languages, "
                        "English Literature and Creative Writing, and Film Studies"
                        "all have classrooms and brand new facilities for staff and students.</p>",

    "Charles Sikes Building":"<h1>Charles Sikes Building</h1>"
                            "<img src='static/images/CharlesSikesBuilding.jpg' width=400px>"
                            "<p>The building houses various academic departments "
                            "and features the Diamond Jubilee Lecture Theatre (CS1/01),"
                            "a modern facility used for lectures and events. "
                            "Situated adjacent to the Huddersfield Narrow Canal, "
                            "the Charles Sikes Building exemplifies the university's blend "
                            "of historical significance and contemporary educational facilities.</p>",

    "Spärck Jones Building":"<h1>Spärck Jones Building</h1>"
                            "<img src='static/images/SparckJonesBuilding.jpg' width=400px>"
                            "<p>The Spärck Jones Building houses Computing and Engineering"
                            "departments, featuring modern laboratories and student support offices. "
                            "It honors Karen Spärck Jones, a pioneer in computer science.</p>",

    "Richard Steinitz Building": "<h1>Richard Steinitz Building</h1>"
                                 "<img src='static/images/RichardSteinitzBuilding.jpg' width=400px>"
                                 "<p>The Richard Steinitz Building contains some of the most extensive"
                                 "Higher Education music facilities in Europe. You'll study in a"
                                 "state-of-the-art learning environment on professional-standard"
                                 "equipment, supported by staff with a blend "
                                "of industry experience and research excellence.</p>",

    "Harold Wilson Building": "<h1>Harold Wilson Building</h1>"
                              "<img src='static/images/HaroldWilsonBuilding.jpg' width=400px>"
                              "<p>The Harold Wilson Building houses various academic departments "
                            "and student services, contributing to the university's dynamic learning environment. "
                            "Its central location ensures easy access to other campus facilities and the "
                            "town center, enhancing the overall student experience. </p>",

    "Haslett Building": "<h1>Haslett Building</h1>"
                        "<img src='static/images/HaslettBuilding.jpg' width=400px>"
                        "<p>The Haslett Building, formerly the Firth Street Woollen Mill built in 1865, has been converted into a modern educational facility. "
                        "It now houses various academic departments, reflecting the University of Huddersfield's commitment to preserving industrial heritage while providing contemporary learning environments. "
                        "The building is named in honor of Dame Caroline Haslett, a pioneering electrical engineer and advocate for women's technical education.</p>",

    "Barbara Hepworth Building": "<h1>Barbara Hepworth Building</h1>"
                                 "<img src='static/images/BarbaraHepworthBuilding.jpg' width=400px>"
                                 "<p>The Barbara Hepworth Building houses art, design, and architecture departments. "
                                "It offers modern facilities for creative students, providing spaces for exhibitions, studios, and collaborative work. "
                                "The building is named after the renowned British sculptor Barbara Hepworth, whose works have left a lasting impact on the art world.</p>",

    "Laura Annie Wilson Building": "<h1>Laura Annie Wilson Building</h1>"
                                   "<img src='static/images/LauraAnneWilsonBuilding.jpg' width=400px>"
                                   "<p>The Laura Annie Wilson Building houses various academic departments and provides modern learning spaces. "
                                    "It is dedicated to fostering a dynamic and collaborative environment for students and staff alike. The building "
                                    "is named after Laura Annie Wilson, a pioneering figure in education and women's advocacy.</p>",
}


def create_map(start_coords=None, dest_coords=None):
    # Create a Folium map centered around the university
    campus_map = folium.Map(location=[53.6429, -1.777], zoom_start=16)

    # Add the university boundary to the map
    boundary = ox.geocode_to_gdf("University of Huddersfield")['geometry'].iloc[0]
    folium.GeoJson(boundary).add_to(campus_map)

    # Add markers for each building
    for building, coords in buildings.items():
        folium.Marker(
            location=coords,
            popup=folium.Popup(building_info[building], max_width="100%"),
            tooltip=building,
            icon=folium.Icon(icon='star', icon_color='red')
        ).add_to(campus_map)

    # If start and destination coordinates are provided, add the route
    if start_coords and dest_coords:
        G = ox.graph_from_place("University of Huddersfield, UK", network_type="walk")

        # Calculate the nearest nodes
        orig_node = ox.nearest_nodes(G, start_coords[1], start_coords[0])
        dest_node = ox.nearest_nodes(G, dest_coords[1], dest_coords[0])

        # Calculate the route
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')
        route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

        # Add route to the map
        folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7, tooltip="Route").add_to(campus_map)

        # Add markers for start and destination
        folium.Marker(location=start_coords, tooltip="Start Location", icon=folium.Icon(color='green')).add_to(
            campus_map)
        folium.Marker(location=dest_coords, tooltip="Destination Location", icon=folium.Icon(color='orange')).add_to(
            campus_map)

    return campus_map


@app.route('/', methods=['GET', 'POST'])
def index():
    map_html = ""
    if request.method == 'POST':
        start_building = request.form['from']
        dest_building = request.form['to']

        start_coords = buildings[start_building]
        dest_coords = buildings[dest_building]

        campus_map = create_map(start_coords, dest_coords)
        map_html = campus_map._repr_html_()
    else:
        # Load map centered on the University of Huddersfield without any routes
        campus_map = create_map()
        map_html = campus_map._repr_html_()

    return render_template('index.html', buildings=buildings.keys(), map_html=map_html)


if __name__ == '__main__':
    app.run(debug=True)