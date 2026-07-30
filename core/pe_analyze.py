"""Analyse de fichiers PE (Portable Executable) - sans dependance externe"""

import struct, os, datetime, hashlib

def analyser(chemin):
    if not os.path.isfile(chemin):
        return "Fichier introuvable"
    try:
        with open(chemin, "rb") as f:
            data = f.read()
    except:
        return "Erreur lecture"

    resultats = [f"Analyse PE: {os.path.basename(chemin)}"]

    if len(data) < 64:
        return "Fichier trop petit pour etre un PE"

    if data[:2] == b"MZ":
        resultats.append("Signature MZ: OK")
    else:
        return "Pas un fichier PE valide (pas de signature MZ)"

    try:
        pe_offset = struct.unpack("<I", data[60:64])[0]
        if data[pe_offset:pe_offset+4] == b"PE\x00\x00":
            resultats.append("Signature PE: OK")
        else:
            return "Signature PE manquante"
    except:
        return "Erreur lecture header PE"

    try:
        machine = struct.unpack("<H", data[pe_offset+4:pe_offset+6])[0]
        machines = {0x14c: "x86 (I386)", 0x8664: "x64 (AMD64)", 0x1c4: "ARM64", 0xaa64: "ARM64 (AARCH64)", 0x200: "Itanium"}
        resultats.append(f"Architecture: {machines.get(machine, f'0x{machine:x}')}")

        sections = struct.unpack("<H", data[pe_offset+6:pe_offset+8])[0]
        resultats.append(f"Sections: {sections}")

        timestamp = struct.unpack("<I", data[pe_offset+8:pe_offset+12])[0]
        if timestamp:
            dt = datetime.datetime.fromtimestamp(timestamp)
            resultats.append(f"Compile: {dt}")
    except:
        pass

    try:
        opt_header_offset = pe_offset + 24
        magic = struct.unpack("<H", data[opt_header_offset:opt_header_offset+2])[0]
        if magic == 0x10b:
            resultats.append("Format: PE32")
        elif magic == 0x20b:
            resultats.append("Format: PE32+")
    except:
        pass

    try:
        h = hashlib.sha256()
        with open(chemin, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        resultats.append(f"SHA256: {h.hexdigest()[:64]}")
    except:
        pass

    try:
        taille = os.path.getsize(chemin)
        resultats.append(f"Taille: {taille} octets ({round(taille/1024)} KB)")
    except:
        pass

    return "\n".join(resultats)
