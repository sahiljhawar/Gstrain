import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row, layout
from bokeh.models import Slider, ColumnDataSource, Select, Div
from pycbc.waveform import get_td_waveform
from pycbc.detector import Detector

from pycbc.waveform import td_approximants

TD_APPROXIMANTS = td_approximants()
div = Div(
    text="<h2><br><br>While using certain combination of parameters and approximants the plot may feel stuck, this is due to limited domain of these approximants (see your terminal of exact errors and refer to LALSimulation)</h2>", width=600)


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
    detectors: list[str] = ["H1", "V1", "L1", "All"],
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

    det_h1 = Detector("H1")
    det_l1 = Detector("L1")
    det_v1 = Detector("V1")

    all_waveforms = {}

    for det in detectors:
        if det == "H1":
            det_h1 = Detector("H1")
            signal_h1 = det_h1.project_wave(hp, hc, ra, dec, polarization)
            all_waveforms[det] = signal_h1
        elif det == "L1":
            det_l1 = Detector("L1")
            signal_l1 = det_l1.project_wave(hp, hc, ra, dec, polarization)
            all_waveforms[det] = signal_l1
        elif det == "V1":
            det_v1 = Detector("V1")
            signal_v1 = det_v1.project_wave(hp, hc, ra, dec, polarization)
            all_waveforms[det] = signal_v1
        elif det == "All":
            det_h1 = Detector("H1")
            signal_h1 = det_h1.project_wave(hp, hc, ra, dec, polarization)
            det_l1 = Detector("L1")
            signal_l1 = det_l1.project_wave(hp, hc, ra, dec, polarization)
            det_v1 = Detector("V1")
            signal_v1 = det_v1.project_wave(hp, hc, ra, dec, polarization)
            all_waveforms["H1"] = signal_h1
            all_waveforms["L1"] = signal_l1
            all_waveforms["V1"] = signal_v1

    return hp.sample_times, all_waveforms


times, all_waveforms = generate_waveform(
    "IMRPhenomPv3", 2.4, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0
)

source = ColumnDataSource(
    data={
        "x": times,
        "y1": all_waveforms["H1"],
        "y2": all_waveforms["L1"],
        "y3": all_waveforms["V1"],
    }
)

p = figure(
    title="Gravitational Wave Strain",
    x_axis_label="Time (s)",
    y_axis_label="Strain",
    width=1500,
    height=500,
    x_range=(-0.4, 0.1),
)
p.title.text_font_size = '20pt'
p.xaxis.axis_label_text_font_size = "15pt"
p.yaxis.axis_label_text_font_size = "15pt"

p.line("x", "y1", source=source, legend_label="H1", color="blue")
p.line("x", "y2", source=source, legend_label="L1", color="red", line_dash="dashed")
p.line("x", "y3", source=source, legend_label="V1", color="green", line_dash="dotted")


q_slider = Slider(start=1.0, end=5.0, step=0.1, value=2.4, title="Mass Ratio (q)")
chiAx_slider = Slider(
    start=-1, end=1, step=0.05, value=0.0, title="Spin1 x-component $$\chi^1_x$$"
)
chiAy_slider = Slider(
    start=-1, end=1, step=0.05, value=0, title=r"Spin1 y-component $$\chi^1_y$$"
)
chiAz_slider = Slider(
    start=-1, end=1, step=0.05, value=0, title=r"Spin1 z-component $$\chi^1_z$$"
)
chiBx_slider = Slider(
    start=-1, end=1, step=0.05, value=0, title=r"Spin2 x-component $$\chi^2_x$$"
)
chiBy_slider = Slider(
    start=-1, end=1, step=0.05, value=0, title=r"Spin2 y-component $$\chi^2_y$$"
)
chiBz_slider = Slider(
    start=-1, end=1, step=0.05, value=0, title=r"Spin2 z-component $$\chi^2_z$$"
)
iota_slider = Slider(
    start=0, end=np.pi, step=np.pi / 18, value=0, title=r"Inclination $$\iota$$"
)
phi_ref_slider = Slider(
    start=0,
    end=np.pi,
    step=np.pi / 18,
    value=0,
    title=r"Azimuthal Angle $$\phi_{ref}$$",
)


ra_slider = Slider(
    start=0, end=2 * np.pi, step=0.01, value=0.5, title="Right Ascension (ra)"
)
dec_slider = Slider(
    start=-np.pi / 2, end=np.pi / 2, step=0.01, value=0.0, title="Declination (dec)"
)
polarization_slider = Slider(
    start=0, end=np.pi, step=0.01, value=0.0, title="Polarization Angle (polarization)"
)


detector_select = Select(
    title="Detector", value="All", options=["H1", "L1", "V1", "All"]
)
approximant_select = Select(
    title="Approximant",
    value="IMRPhenomPv3",
    options=TD_APPROXIMANTS,
)


def update(attr, old, new):
    times, all_waveforms = generate_waveform(
        approximant_select.value,
        q_slider.value,
        chiAx_slider.value,
        chiAy_slider.value,
        chiAz_slider.value,
        chiBx_slider.value,
        chiBy_slider.value,
        chiBz_slider.value,
        iota_slider.value,
        phi_ref_slider.value,
        ra_slider.value,
        dec_slider.value,
        polarization_slider.value,
    )

    p.legend.visible = False
    if detector_select.value == "H1":
        source.data = {"x": times, "y1": all_waveforms["H1"]}
    elif detector_select.value == "L1":
        source.data = {"x": times, "y1": all_waveforms["L1"]}
    elif detector_select.value == "V1":
        source.data = {"x": times, "y1": all_waveforms["V1"]}
    else:
        source.data = {
            "x": times,
            "y1": all_waveforms["H1"],
            "y2": all_waveforms["L1"],
            "y3": all_waveforms["V1"],
        }
        p.legend.visible = True


for slider in [
    q_slider,
    chiAx_slider,
    chiAy_slider,
    chiAz_slider,
    chiBx_slider,
    chiBy_slider,
    chiBz_slider,
    iota_slider,
    phi_ref_slider,
    ra_slider,
    dec_slider,
    polarization_slider,
    detector_select,
    approximant_select,
]:
    slider.on_change("value", update)

sliders = column(
    row(detector_select, approximant_select),
    row(q_slider, iota_slider, phi_ref_slider),
    row(chiAx_slider, chiAy_slider, chiAz_slider),
    row(chiBx_slider, chiBy_slider, chiBz_slider),
    row(ra_slider, dec_slider, polarization_slider),
)

web_layout = layout(
    [p],
    [sliders, div]
)

curdoc().add_root(web_layout)
