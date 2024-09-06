import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import os
from dotenv import load_dotenv
from io import BytesIO
import base64

# Set page configuration as the first Streamlit command
st.set_page_config(layout="wide", page_title="SDOH Locations Map", page_icon="🗺️")

# Load environment variables
load_dotenv()

# Get Google Maps API key
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Geocoder function
def geocode_address(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        st.error(f"Geocoding failed for address: {address}")
        return None

# Save Folium map as HTML
def save_map(m):
    map_data = BytesIO()
    m.save(map_data, close_file=False)
    return map_data.getvalue().decode()

# Create a download link for the HTML file
def download_link(data, filename, text):
    b64 = base64.b64encode(data.encode()).decode()  # Encode the HTML to base64
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Initialize session state for locations and language
if 'locations' not in st.session_state:
    st.session_state.locations = [
        {"name": "Nueva Colombia, Barranquilla, Atlántico, Colombia", "label_offset": [-0.05, -0.02]},
        {"name": "El Valle, Atlántico, Colombia", "label_offset": [0.07, 0.06]},
        {"name": "San José de Saco, Juan de Acosta, Atlántico, Colombia", "label_offset": [0, 0]},
        {"name": "Blas de Lezo, Cartagena, Cartagena Province, Bolivar, Colombia", "label_offset": [0, 0]},
        {"name": "Loma de Arena, Santa Catalina, Bolivar, Colombia", "label_offset": [0, 0]},
        {"name": "Pontezuela, Cartagena, Cartagena Province, Bolivar, Colombia", "label_offset": [0, 0]},
        {"name": "Maicao, La Guajira, Colombia", "label_offset": [0, 0]},
        {"name": "Rancheria, Rioacha, La Guajira, Colombia", "label_offset": [0, 0]}
    ]

if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Language dictionary
lang_dict = {
    'English': {
        'title': 'Interactive Map of SDOH Locations',
        'add_location': 'Add a new location:',
        'adjust_position': 'Adjust position for',
        'text_customization': 'Customize Labels',
        'select_color': 'Select label text color',
        'select_size': 'Select label text size (pt)',
        'adjust_positions': 'Adjust Label Positions',
        'remove': 'Remove',
        'download_map': 'Download Map',
        'translate': 'En/Es'
    },
    'Spanish': {
        'title': 'Mapa interactivo de ubicaciones de SDOH',
        'add_location': 'Agregar nueva ubicación:',
        'adjust_position': 'Ajustar posición para',
        'text_customization': 'Personalizar etiquetas',
        'select_color': 'Seleccionar color de texto de la etiqueta',
        'select_size': 'Seleccionar tamaño de texto de la etiqueta (pt)',
        'adjust_positions': 'Ajustar posiciones de las etiquetas',
        'remove': 'Eliminar',
        'download_map': 'Descargar mapa',
        'translate': 'En/Es'
    }
}

# Switch between English and Spanish
if st.button(lang_dict[st.session_state.language]['translate']):
    if st.session_state.language == 'English':
        st.session_state.language = 'Spanish'
    else:
        st.session_state.language = 'English'

# Access the current language
current_lang = lang_dict[st.session_state.language]

# Title with improved styling
st.markdown(f"<h1 style='text-align: center; color: #2c3e50;'>{current_lang['title']}</h1>", unsafe_allow_html=True)


# Create three columns: controls on the left, map in the center, sliders on the right
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    # Add new location input at the top
    st.markdown(f"#### {current_lang['add_location']}")
    new_location = st.text_input(current_lang['add_location'], key="new_location_input")
    if st.button("➕ Add Location"):
        if new_location:
            st.session_state.locations.append({"name": new_location, "label_offset": [0.0, 0.0]})
            st.success(f"✅ {new_location} added!")
    
    st.markdown("---")
    
    # Text Customization section
    st.markdown(f"#### {current_lang['text_customization']}")
    
    # Sidebar for color picker and text size
    text_color = st.color_picker(current_lang['select_color'], value="#800000")  # Default color is dark red
    text_size = st.slider(current_lang['select_size'], 6, 20, 8)  # Default size is 8pt
    
    st.markdown("---")
    # Remove button for locations
    for idx, location in enumerate(st.session_state.locations):
        if st.button(f"❌ {current_lang['remove']} {location['name'].split(',')[0]}", key=f"remove_{idx}"):
            removed_location = st.session_state.locations.pop(idx)
            st.success(f"✅ {removed_location['name']} removed!")

with col2:
    # Create map
    m = folium.Map(
        location=[10.6966, -74.8741],
        zoom_start=9,
        tiles='CartoDB positron',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    )

    # Add markers and labels
    for location in st.session_state.locations:
        coordinates = geocode_address(location['name'])
        if coordinates:
            # Ensure label_offset exists and is a list of floats
            if 'label_offset' not in location or not isinstance(location['label_offset'], list) or len(location['label_offset']) != 2:
                location['label_offset'] = [0.0, 0.0]
            
            # Add marker
            folium.Marker(
                location=coordinates,
                popup=folium.Popup(location['name'], parse_html=True),
                icon=folium.features.CustomIcon(
                    icon_image='https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png',
                    icon_size=(20, 20),
                    icon_anchor=(10, 20),
                    popup_anchor=(0, -20)
                )
            ).add_to(m)
            
            # Add label with custom color and size
            label_lat = coordinates[0] + location['label_offset'][0]
            label_lon = coordinates[1] + location['label_offset'][1]
            folium.map.Marker(
                [label_lat, label_lon],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: {text_size}pt; color: {text_color}; text-shadow: 1px 1px 1px #FFFFFF; line-height: 1;">{location["name"].split(",")[0]}</div>'
                )
            ).add_to(m)
    
    # Display the map
    folium_static(m, width=800, height=600)

    # Save and provide download link
    map_html = save_map(m)
    st.markdown(download_link(map_html, "interactive_map.html", f"📥 {current_lang['download_map']}"), unsafe_allow_html=True)

with col3:
    # Sliders for adjusting label positions
    st.markdown(f"#### {current_lang['adjust_positions']}")
    locations_to_remove = []
    for idx, location in enumerate(st.session_state.locations):
        st.write(f"{current_lang['adjust_position']} {location['name'].split(',')[0]}:")
        col_lat, col_lon = st.columns(2)
        with col_lat:
            lat_offset = st.slider(f"Lat {idx}", -0.1, 0.1, float(location['label_offset'][0]), 0.001, key=f"lat_{idx}")
        with col_lon:
            lon_offset = st.slider(f"Lon {idx}", -0.1, 0.1, float(location['label_offset'][1]), 0.001, key=f"lon_{idx}")
        st.session_state.locations[idx]['label_offset'] = [lat_offset, lon_offset]

    st.markdown("---")
    
# Add a footer
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d; padding: 10px;'>
        © 2024 SDOH Locations Map | Created by Maria Aroca
    </div>
    """,
    unsafe_allow_html=True
)


