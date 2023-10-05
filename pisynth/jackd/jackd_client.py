from dataclasses import dataclass
import enum
from enum import _EnumDict
import re

from typing import Any, Dict, Iterable, List, Union
import jack

SAME_NAME_CHANNELS = {
    "FR": ["FR", "RIGHT", "FRONTRIGHT"],
    "FL": ["FL", "LEFT", "FRONTLEFT"],
    "BR": ["BR", "REARRIGHT", "BACKRIGHT", "RR"],
    "BL": ["BL", "REARLEFT", "BACKLEFT", "RL"],
    "C": ["C", "CENTER", "CENTRE"],
}

class AudioChannel(str, enum.Enum):
    FR = "FR"
    FL = "FL"
    BR = "BR"
    BL = "BL"
    C = "C"
    
    # def __new__(cls, value):
    #     for key, values in SAME_NAME_CHANNELS.items():
    #         if value in values:
    #             obj = str.__new__(cls)
    #             obj._value_ = key
    #             for v in values:
    #                 cls._value2member_map_[v] = obj 
                    
    #             obj._all_values = values
    #     return super().__new__(cls, value)

    def __eq__(self, __value) -> bool:
        if isinstance(__value, str):
            return self._value_ == __value.upper()
        if isinstance(__value, AudioChannel):
            return self._value_ == __value._value_
        return False
    
    @classmethod
    def _missing_(cls, value):
        value = value.upper()
        for member in cls:
            if value in SAME_NAME_CHANNELS[member._value_]:
                return member
        return None

    def __hash__(self) -> int:
        return self._value_.__hash__()


_CLIENT = jack.Client("pysynth")

def rev(in_str: str) -> str:
    return in_str[::-1]

def _get_channel(in_str: Union[str, jack.Port]) -> AudioChannel:
    if isinstance(in_str, jack.Port):
        in_str = in_str.name
    return AudioChannel(rev(re.split(':|_', rev(in_str), maxsplit=1)[0]))

def _get_name_without_channel(in_str: str) -> str:
    return rev(':'.join(re.split(':|_', rev(in_str), maxsplit=1)[1:]))

@dataclass
class QSynth:
    
    midi_in: Dict[str, jack.MidiPort]
    audio_out: Dict[str, jack.Port]
    
    def connect_midi_input(self, port: Union[jack.MidiPort, str] ):
        client = get_client()
        for in_port in self.midi_in:
            for c in client.get_all_connections(in_port):
                    client.disconnect(c, in_port)
            client.connect(port, in_port)

    
    def connect_audio_output(self, port: Union[jack.Port, str] ):
        client = get_client()
        port_name = port if isinstance(port, str) else port.name
        outputs = [v for k, v in get_default_outputs().items() if port_name in k]
        if len(outputs) == 0:
            raise ValueError("Port not found")
        
        outputs = outputs[0]  # take first output
        if len(outputs)==1: # mono
            for out_port in self.audio_out:
                for c in client.get_all_connections(out_port):
                    client.disconnect(out_port, c)
                client.connect(out_port, port)
        if len(outputs)>1: # multiple
            channels_to_name = _build_channels_to_name_map(outputs)
            for out_port in self.audio_out:
                for c in client.get_all_connections(out_port):
                    client.disconnect(out_port, c)
                ch = _get_channel(out_port)
                client.connect(out_port, channels_to_name[ch])
            


    def check_connections(self):
        pass

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

def get_default_outputs(stereo=True) -> Dict[str, jack.Port]:
    outputs = get_audio_ports(input=True)
    if not stereo:    
        return outputs
    keys = set(_get_name_without_channel(n) for n in outputs)
    return {k: [v for _, v in outputs.items() if k in _] for k in keys}
    
def _build_channels_to_name_map(outputs: Dict[str, jack.Port]) -> Dict[AudioChannel, str]:
    return {_get_channel(key): key for key in outputs}
    