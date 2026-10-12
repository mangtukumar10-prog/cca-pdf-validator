import os
import io
import pypdf

def extract_all_signature_dicts(reader: pypdf.PdfReader):
    found = []
    seen_ranges = set()

    def check_sig_obj(obj, name_hint="Signature"):
        if not obj or not hasattr(obj, 'get'):
            return
        target = obj
        if '/V' in obj:
            v = obj['/V']
            target = v.get_object() if hasattr(v, 'get_object') else v
        elif obj.get('/Type') == '/Sig':
            target = obj
        
        if target and hasattr(target, 'get') and '/ByteRange' in target and '/Contents' in target:
            try:
                br = tuple(int(x) for x in target['/ByteRange'])
                if br not in seen_ranges:
                    seen_ranges.add(br)
                    sig_entry = dict(target)
                    sig_entry['/T'] = target.get('/T') or name_hint
                    sig_entry['/ByteRange'] = list(br)
                    found.append(sig_entry)
            except Exception:
                pass

    # 1. Walk AcroForm fields
    try:
        trailer = reader.trailer
        root = trailer.get('/Root', {})
        if hasattr(root, 'get_object'): root = root.get_object()
        acro = root.get('/AcroForm', {})
        if hasattr(acro, 'get_object'): acro = acro.get_object()
        
        def walk_fields(fields):
            for f in fields:
                f_obj = f.get_object() if hasattr(f, 'get_object') else f
                if not f_obj: continue
                hint = str(f_obj.get('/T', 'Signature'))
                if f_obj.get('/FT') == '/Sig' or '/V' in f_obj:
                    check_sig_obj(f_obj, hint)
                kids = f_obj.get('/Kids', [])
                if kids:
                    walk_fields(kids)

        walk_fields(acro.get('/Fields', []))
    except Exception:
        pass

    # 2. Walk Page Annots
    try:
        for p in reader.pages:
            annots = p.get('/Annots', [])
            if hasattr(annots, 'get_object'): annots = annots.get_object()
            if not annots: continue
            for a in annots:
                a_obj = a.get_object() if hasattr(a, 'get_object') else a
                if not a_obj: continue
                if a_obj.get('/FT') == '/Sig' or a_obj.get('/Type') == '/Sig' or '/V' in a_obj:
                    hint = str(a_obj.get('/T', 'Signature'))
                    check_sig_obj(a_obj, hint)
    except Exception:
        pass

    return found

# Test with vivan certificate
r = pypdf.PdfReader('vivan_birth_certificate_original_signed.pdf')
sigs = extract_all_signature_dicts(r)
print(f"Extracted {len(sigs)} signatures:")
for s in sigs:
    print("  - Field:", s.get('/T'), "SubFilter:", s.get('/SubFilter'), "ByteRange:", s.get('/ByteRange'))
