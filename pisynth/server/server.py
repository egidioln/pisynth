from pathlib import Path
from logging import getLogger

from flask import Flask, request, render_template

from pisynth.jackd.jackd_client import get_client, get_midi_ports, get_qsynth, get_default_outputs

logger = getLogger(__name__)
logger.setLevel("INFO")
app = Flask(__name__)
current_path = Path(__file__).parent
index_path = "index.html"
qsynth = None
output_device = None

# Initialize some default parameters
parameters = {
    "slider_value": 50,
    "checkbox_status": False,
    "midi_device": None,
    "output_device": None,
}


@app.route("/", methods=["GET", "POST"])
def index():

    midi_ports = get_midi_ports(output=True)
    outputs = get_default_outputs()
    qsynth.check_connections()
    if request.method == "POST":
        # Update parameters based on form data
        logger.info(request.form)
        parameters["slider_value"] = int(request.form["slider"])
        parameters["checkbox_status"] = "checkbox" in request.form
        if parameters["midi_device"] != request.form["midi_device"]:
            parameters["midi_device"] = request.form["midi_device"]
            qsynth.connect_midi_input(request.form["midi_device"])
        
        if parameters["output_device"] != request.form["output_device"]:
            parameters["output_device"] = request.form["output_device"]
            qsynth.connect_audio_output(request.form["output_device"])
        


    return render_template(index_path, parameters=parameters, midi_devices=midi_ports.keys(), output_devices=outputs.keys())

def init():
    global qsynth, output_device
    output_device = get_default_outputs()
    qsynth = get_qsynth()
    app.run(debug=True)
    
if __name__ == "__main__":
    init()
    