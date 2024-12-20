import streamlit as st
import os
import zipfile
import math
from tempfile import TemporaryDirectory
from OCC.Display.OCCViewer import Viewer3d
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.AIS import AIS_Shaded
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.Graphic3d import Graphic3d_RenderingParams

def generate_spherical_views(step=25):
    """
    Generuje pohledy rovnoměrně rozložené po povrchu sféry.
    :param step: Krok v úhlech (\u00b0) pro azimut a nadmořskou výšku.
    :return: Seznam trojic (x, y, z) reprezentujících směry pohledu.
    """
    views = []
    for elevation in range(-90, 91, step):  # Od -90\u00b0 (spodní pohled) po 90\u00b0 (horní pohled)
        for azimuth in range(0, 360, step):  # Objeď kolem dokola 360\u00b0
            x = math.cos(math.radians(elevation)) * math.cos(math.radians(azimuth))
            y = math.cos(math.radians(elevation)) * math.sin(math.radians(azimuth))
            z = math.sin(math.radians(elevation))
            views.append((x, y, z))
    return views

def render_offscreen(step_file, output_dir, resolution, progress_bar=None, progress_start=0, progress_end=1):
    """Renderuje STEP soubor do snímků z pohledů generovaných sféricky."""
    st.write(f"Renderuji soubor: {step_file}")
    viewer = Viewer3d()
    viewer.Create(None)
    view = viewer.View
    white_color = Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB)  # Bílé RGB pozadí
    view.SetBackgroundColor(white_color)

    reader = STEPControl_Reader()
    reader.ReadFile(step_file)
    reader.TransferRoot()
    shape = reader.Shape()
    viewer.DisplayShape(shape)

    viewer.Context.SetDisplayMode(AIS_Shaded, True)
    viewer.SetSize(*resolution)  # Nastavení uživatelského rozlišení

    # Fit model to ensure consistent size
    view.FitAll()
    view.ZFitAll()

    views = generate_spherical_views(step=25)  # Pohledy po krocích 25°
    total_views = len(views)
    for i, direction in enumerate(views):
        view.SetProj(*direction)
        view.Redraw()

        # Uložení snímku
        output_file = os.path.join(output_dir, f"view_{i + 1}.png")
        params = Graphic3d_RenderingParams()
        view.Dump(output_file)

        # Aktualizace průběhu
        if progress_bar:
            progress_fraction = progress_start + (i + 1) / total_views * (progress_end - progress_start)
            progress_bar.progress(progress_fraction)

def create_zip_from_results(temp_dir, zip_name):
    """Vytvoří ZIP soubor s výsledky."""
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_dir))
    return zip_name

# Streamlit UI
st.title("Batch STEP File Renderer")
tabs = st.tabs(["Main", "Settings"])

# Tab: Settings
with tabs[1]:
    st.header("Nastavení rozlišení")
    if "resolution" not in st.session_state:
        st.session_state["resolution"] = (500, 500)  # Výchozí rozlišení

    width = st.number_input(
        "Šířka rozlišení (px):",
        min_value=100,
        max_value=3840,
        value=st.session_state["resolution"][0],
        key="resolution_width"
    )
    height = st.number_input(
        "Výška rozlišení (px):",
        min_value=100,
        max_value=2160,
        value=st.session_state["resolution"][1],
        key="resolution_height"
    )
    st.session_state["resolution"] = (width, height)

# Tab: Main
with tabs[0]:
    st.header("Hlavní")
    st.write("Nahrajte STEP soubory, generujte snímky z různých pohledů a stáhněte výsledky jako ZIP.")

    if "processing_done" not in st.session_state:
        st.session_state["processing_done"] = False

    if "output_zip" not in st.session_state:
        st.session_state["output_zip"] = None

    uploaded_files = st.file_uploader("Nahrajte STEP soubory", type=["step", "stp"], accept_multiple_files=True)

    if uploaded_files and not st.session_state["processing_done"]:
        with TemporaryDirectory() as temp_dir:
            progress_bar = st.progress(0)
            total_files = len(uploaded_files)

            output_zip = "rendered_results.zip"  # ZIP uložíme mimo TemporaryDirectory

            with st.spinner("Zpracovávám soubory, prosím čekejte..."):
                for idx, uploaded_file in enumerate(uploaded_files):
                    file_name = uploaded_file.name
                    file_path = os.path.join(temp_dir, file_name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.read())

                    step_output_dir = os.path.join(temp_dir, os.path.splitext(file_name)[0])
                    os.makedirs(step_output_dir, exist_ok=True)

                    st.write(f"Zpracovávám soubor: {file_name} ...")
                    render_offscreen(
                        file_path,
                        step_output_dir,
                        resolution=st.session_state["resolution"],
                        progress_bar=progress_bar,
                        progress_start=idx / total_files,
                        progress_end=(idx + 1) / total_files
                    )

                st.write("Vytvářím ZIP soubor...")
                create_zip_from_results(temp_dir, output_zip)
                st.session_state["output_zip"] = output_zip

            progress_bar.progress(1.0)
            st.success("Všechny soubory byly úspěšně zpracovány!")
            st.session_state["processing_done"] = True

    if st.session_state["processing_done"] and st.session_state["output_zip"]:
        with open(st.session_state["output_zip"], "rb") as zip_file:
            st.download_button(
                label="Stáhnout ZIP výsledků",
                data=zip_file,
                file_name="rendered_results.zip",
                mime="application/zip"
            )
