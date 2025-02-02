import streamlit as st
import plotly.graph_objects as go
import numpy as np
from PIL import Image

from pycbc.waveform import get_td_waveform, td_approximants
from pycbc.detector import Detector

im = Image.open("./images/gw.png")
st.set_page_config(layout="wide", page_title="Gstrain", page_icon=im)
st.set_option("client.showErrorDetails", True)


st.title("Gravitational Wave Strain Visualization")
st.markdown("""
    Gravitational Wave strain detected by different detectors.
    Adjust the parameters using the sliders to see how they affect the waveform.
""")


if "TD_APPROXIMANTS" not in st.session_state:
    st.session_state.TD_APPROXIMANTS = td_approximants()


def generate_waveform(
    approximant: str,
    q: float,
    chiAx: float,
    chiAy: float,
    chiAz: float,
    chiBx: float,
    chiBy: float,
    chiBz: float,
    iota: float,
    phi_ref: float,
    ra: float,
    dec: float,
    polarization: float,
    delta_t: float = 1.0 / 4096,
    f_lower: float = 15,
    detectors: list[str] = ["H1", "V1", "L1"],
):
    m2 = 30.0
    m1 = q * m2

    hp, hc = get_td_waveform(
        approximant=approximant,
        mass1=m1,
        mass2=m2,
        spin1x=chiAx,
        spin1y=chiAy,
        spin1z=chiAz,
        spin2x=chiBx,
        spin2y=chiBy,
        spin2z=chiBz,
        delta_t=delta_t,
        f_lower=f_lower,
        inclination=iota,
        coa_phase=phi_ref,
    )

    all_waveforms = {}

    for det in detectors:
        detector = Detector(det)
        signal = detector.project_wave(hp, hc, ra, dec, polarization)
        all_waveforms[det] = signal

    return hp.sample_times, all_waveforms


with st.sidebar:
    st.header("Parameters")

    detector = st.selectbox("Detector", ["All", "H1", "L1", "V1"], index=0)

    approximant = st.selectbox(
        "Approximant",
        st.session_state.TD_APPROXIMANTS,
        index=st.session_state.TD_APPROXIMANTS.index("IMRPhenomPv3"),
    )

    q = st.slider("Mass Ratio (q)", 1.0, 5.0, 2.4, 0.1)
    iota = st.slider(r"Inclination $$(\iota)$$", 0.0, np.pi, 0.0, np.pi / 18)
    phi_ref = st.slider(
        r"Azimuthal Angle $$(\phi_{\rm{ref}})$$", 0.0, np.pi, 0.0, np.pi / 18
    )

    st.subheader("Spin Parameters")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Spin 1**")
        chiAx = st.slider(r"$$\chi^1_x$$", -1.0, 1.0, 0.0, 0.05)
        chiAy = st.slider(r"$$\chi^1_y$$", -1.0, 1.0, 0.0, 0.05)
        chiAz = st.slider(r"$$\chi^1_z$$", -1.0, 1.0, 0.0, 0.05)

    with col2:
        st.markdown("**Spin 2**")
        chiBx = st.slider(r"$$\chi^2_x$$", -1.0, 1.0, 0.0, 0.05)
        chiBy = st.slider(r"$$\chi^2_y$$", -1.0, 1.0, 0.0, 0.05)
        chiBz = st.slider(r"$$\chi^2_z$$", -1.0, 1.0, 0.0, 0.05)

    st.subheader("Source Location")
    ra = st.slider("Right Ascension (ra)", 0.0, 2 * np.pi, 0.5, 0.01)
    dec = st.slider("Declination (dec)", -np.pi / 2, np.pi / 2, 0.0, 0.01)
    polarization = st.slider("Polarization Angle", 0.0, np.pi, 0.0, 0.01)


try:
    times, all_waveforms = generate_waveform(
        approximant,
        q,
        chiAx,
        chiAy,
        chiAz,
        chiBx,
        chiBy,
        chiBz,
        iota,
        phi_ref,
        ra,
        dec,
        polarization,
    )

    fig = go.Figure()

    if detector == "All":
        fig.add_trace(
            go.Scatter(
                x=times, y=all_waveforms["H1"], name="H1", line=dict(color="blue")
            )
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=all_waveforms["L1"],
                name="L1",
                line=dict(color="red", dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=all_waveforms["V1"],
                name="V1",
                line=dict(color="green", dash="dot"),
            )
        )
    else:
        fig.add_trace(go.Scatter(x=times, y=all_waveforms[detector], name=detector))

    fig.update_layout(
        title=dict(text="Gravitational Wave Strain", font=dict(size=24)),
        xaxis_title=dict(text="Time (s)", font=dict(size=18)),
        yaxis_title=dict(text="Strain", font=dict(size=18)),
        xaxis=dict(range=[-0.4, 0.1]),
        showlegend=detector == "All",
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("""
        Error generating waveform. This might be due to:
        1. Invalid parameter combination
        2. Approximant limitations""")

    st.exception(e)


st.markdown("""
    While using certain combinations of parameters and approximants, the plot may not generate due to limited domains of these approximants. 
    Please refer to LALSimulation documentation for exact parameter ranges for each approximant.
""")
