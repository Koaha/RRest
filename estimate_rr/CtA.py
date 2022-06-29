import numpy as np
from scipy import signal
from RRest.preprocess.band_filter import BandpassFilter


def preprocess_signal(sig, fs, filter_type="butterworth", highpass=0.1, lowpass=0.5, degree=1, cutoff=False,
                      cutoff_quantile=0.9):
    # Prepare and filter signal
    hp_cutoff_order = [highpass, degree]
    lp_cutoff_order = [lowpass, degree]
    filt = BandpassFilter(band_type=filter_type, fs=fs)
    filtered_segment = filt.signal_highpass_filter(sig, cutoff=hp_cutoff_order[0], order=hp_cutoff_order[1])
    filtered_segment = filt.signal_lowpass_filter(filtered_segment, cutoff=lp_cutoff_order[0], order=lp_cutoff_order[1])
    if cutoff:
        cutoff = np.quantile(np.abs(filtered_segment), cutoff_quantile)
        filtered_segment[np.abs(filtered_segment) < cutoff] = 0
    return filtered_segment


def get_rr(sig, fs, preprocess=True):
    # Step 1 preprocess with butterworth filter - 0.1-0.5 -> depend on the device
    if preprocess:
        # pro_sig = preprocess_signal(sig, fs)
        sig = preprocess_signal(sig, fs)
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=np.arange(len(sig)),y=sig,line=dict(color='blue')))
    # fig.add_trace(go.Scatter(x=np.arange(len(pro_sig)), y=pro_sig,line=dict(color='crimson')))
    # fig.show()
    # Step 2
    local_max = signal.argrelmax(sig, order=1)[0]  # if the diff is greater than 2 continuous points
    local_min = signal.argrelmin(sig, order=1)[0]

    # Step 3 define the local max threshold by taking the 0.75 quantile
    # Compute the subsequent local extrema differences
    resp_markers = get_valid_rr(sig, local_min, local_max)
    print(len(resp_markers))


def get_valid_rr(sig, local_min, local_max):
    extrema_indices = np.sort(list(local_min) + list(local_max))
    extrema_differences = np.abs(np.diff(sig[extrema_indices]))
    # resp_markers = []
    thres = np.quantile(extrema_differences, 0.75) * 0.3

    # Step 4 find the pair of subsequent extrema
    # find the min difference -> if differ < threshold-> split into 2
    # continue 'till all greater
    removing_extrema = True
    while removing_extrema:
        extrema_differences = np.abs(np.diff(sig[extrema_indices]))
        min_diff = np.min(extrema_differences)
        min_ind_diff = np.argmin(extrema_differences)
        if min_diff < thres:
            extrema_indices = np.delete(extrema_indices, [min_ind_diff, min_ind_diff + 1])
        else:
            removing_extrema = False
    rel_peaks = np.intersect1d(extrema_indices, local_max)
    rel_troughs = np.intersect1d(extrema_indices, local_min)

    return rel_peaks, rel_troughs
