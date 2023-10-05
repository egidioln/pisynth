from dataclasses import dataclass

from typing import Dict, List
import jack


_CLIENT = jack.Client("pysynth")


@dataclass
class QSynth:
    midi_in: Dict[str, jack.MidiPort]
    audio_out: Dict[str, jack.Port]


def get_client() -> jack.Client:
    _CLIENT.activate()
    return _CLIENT


def get_midi_ports(input=False, output=False) -> Dict[str, jack.MidiPort]:
    return {
        p.name: p
        for p in get_client().get_ports()
        if isinstance(p, jack.MidiPort)
        and (not input or p.is_input)
        and (not output or p.is_output)
    }


def get_audio_ports(input=False, output=False) -> Dict[str, jack.Port]:
    return {
        p.name: p
        for p in get_client().get_ports()
        if not isinstance(p, jack.MidiPort)
        and (not input or p.is_input)
        and (not output or p.is_output)
    }


def get_qsynth():
    midi_in = {
        name: port
        for name, port in get_midi_ports(input=True).items()
        if "qsynth" in name
    }
    audio_out = {
        name: port
        for name, port in get_audio_ports(output=True).items()
        if "qsynth" in name
    }

    return QSynth(midi_in=midi_in, audio_out=audio_out)

def get_default_output() -> Dict[str, jack.Port]:
    outputs = get_audio_ports(input=True)
    return outputs