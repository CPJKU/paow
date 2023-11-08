import partitura as pt
import numpy as np
import glob
import os
from collections import defaultdict

def split_by_voice(pna, alignment, sna):
    matched_idxs = pt.musicanalysis.performance_codec.get_matched_notes(sna, pna,
                                                                        alignment)
    voices = np.unique(sna["voice"])
    voice_number_of_notes = np.zeros_like(voices)
    for id, voice in enumerate(voices):
        mask = np.where(sna["voice"] == voice)[0]
        voice_number_of_notes[id] = len(mask)

    pna_idxs = np.arange(len(pna))
    voice_sort_idx = np.argsort(voice_number_of_notes)
    collect_pna_masks = list()

    # collect the five largest
    for voice in voices[voice_sort_idx[-1:-6:-1]]:
        idxs_for_voice = np.where(sna["voice"] == voice)[0]
        pna_mask = np.zeros_like(pna_idxs).astype(bool)
        for idx in idxs_for_voice:
            matched_mask_for_voice = np.where(matched_idxs[:,0] == idx)[0]
            perf_idx = matched_idxs[matched_mask_for_voice,1]
            if len(perf_idx) == 1:
                mask_pna_idx = np.where(perf_idx == pna_idxs)[0]
                pna_mask[mask_pna_idx] = True
        collect_pna_masks.append(pna_mask)

    # all the remaining ones in a single voice
    if len(voices) >= 6:
        pna_mask = np.zeros_like(pna_idxs).astype(bool)
        for voice in voices[voice_sort_idx[:-5]]:
            idxs_for_voice = np.where(sna["voice"] == voice)[0]
            for idx in idxs_for_voice:
                matched_mask_for_voice = np.where(matched_idxs[:,0] == idx)[0]
                perf_idx = matched_idxs[matched_mask_for_voice,1]
                if len(perf_idx) == 1:
                    mask_pna_idx = np.where(perf_idx == pna_idxs)[0]
                    pna_mask[mask_pna_idx] = True
        collect_pna_masks.append(pna_mask)

    return collect_pna_masks

if __name__ == "__main__":

    nasap = r"PATH_TO_ASAP\asap-dataset\Bach\Fugue\*\*.match"
    outdir = r"PATH_TO_OUTPUT_DIR"
    perpiece = defaultdict(list)
    random_perpiece = list
    RNG = np.random.default_rng(seed=2222)

    for file in glob.glob(nasap):
        perpiece[os.path.dirname(file)].append(os.path.basename(file))

    chosen = list()
    for dir in list(perpiece.keys()):
        file_c = RNG.choice(perpiece[dir])
        perf, alignment, score = pt.load_match(os.path.join(dir,file_c), create_score = True)
        sna = score[0].note_array() 
        pna = perf[0].note_array() 
        collect_pna_masks = split_by_voice(pna, alignment, sna)

        # get pna corresponding to voices
        for voice_idx, voice_mask in enumerate(collect_pna_masks):
            # create a performedpart from the collected notes
            performed_part = pt.performance.PerformedPart.from_note_array(pna[voice_mask])
            # save it 
            pt.save_performance_midi(performed_part, 
                                     os.path.join(outdir, 
                                                  "{0}_voice_{1}.mid".format(file_c, voice_idx)))


    