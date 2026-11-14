#!/usr/bin/env python3
"""make_eprom_1541.py - EPROM-Vorlage C1541_29F040.BIN fuer den 1541 Multi-Speeder V3.

8 Baenke zu 64 KB, n@RNROM waehlt Bank n. Jede Bank bildet den Adressraum der
1541 direkt ab (Bank-Anfang + $xxxx = CPU-Adresse $xxxx); ungenutzte Bereiche $FF.
Der Adressdecoder blendet in den Baenken 1-4 RAM bei $4000-$9FFF ein (ohne PIA,
RAMBoard-Modus), in den Baenken 5-8 den PIA bei $5000, das 8-KB-RAM-Fenster bei
$6000-$7FFF und ROM bei $8000-$FFFF. DolphinDos26 braucht den PIA -> Bank 5-8.

  Bank 1, 3-6  Commodore DOS 2.6 (325302-01 + 901229-05)  $xC000-$xFFFF
  Bank 2       DolphinDOS 2.0 (Original, RAM bei $6000)   $1A000-$1FFFF
  Bank 7       DolphinDos26DD2 (Parallelkabel am VIA1)     $60000-$6FFFF
  Bank 8       DolphinDos26 (Parallelkabel am PIA)         $70000-$7FFFF

Kein JiffyDOS. Aufruf: tools/make_eprom_1541.py [ausgabe]
(Standard: rom/C1541_29F040.BIN). Quellen ueber das Projektverzeichnis mit Builds/.
"""
import hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def root():
    d = REPO
    while d != '/':
        if os.path.isdir(os.path.join(d, 'Builds')) and os.path.isdir(os.path.join(d, 'Referenzen')):
            return d
        d = os.path.dirname(d)
    sys.exit('Projektverzeichnis mit Builds/ nicht gefunden')


R = root()
SRC = {
    'cbm': (os.path.expanduser('~/.local/vice-ms/share/vice/DRIVES/dos1541-325302-01+901229-05.bin'), 0x4000,
            'a0ce8439d1b8dcf2e1430461f7233a72'),
    'dd2': (os.path.join(R, 'Referenzen', 'DolphinDos2-6000.bin'), 0x8000,
            'd55c5a1a5bd78874037dcb01de11d162'),
    'dd26dd2': (os.path.join(R, 'Builds', 'C1541_DOLPHINDOS26DD2.bin'), 0x10000, None),
    'dd26': (os.path.join(R, 'Builds', '1541DolphinDos26.bin'), 0x10000, None),
}
BANKS = ['cbm', 'dd2', 'cbm', 'cbm', 'cbm', 'cbm', 'dd26dd2', 'dd26']


def load(k):
    p, size, md5 = SRC[k]
    d = open(p, 'rb').read()
    if len(d) != size:
        sys.exit('%s: %d Bytes statt %d' % (p, len(d), size))
    if md5 and hashlib.md5(d).hexdigest() != md5:
        sys.exit('%s: falsche Pruefsumme' % p)
    if b'JIFFY' in d.upper():
        sys.exit('%s: enthaelt JiffyDOS-Text, nicht erlaubt' % p)
    return d


out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, 'rom', 'C1541_29F040.BIN')
img = bytearray()
for k in BANKS:
    d = load(k)
    img += b'\xff' * (0x10000 - len(d)) + d
assert len(img) == 0x80000
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'wb').write(img)
print('%s  %s' % (hashlib.md5(img).hexdigest(), out))
