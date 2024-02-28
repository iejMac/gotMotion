from scipy.stats import spearmanr


def ranking_correlation(motion_est, motion_gt):
    return spearmanr(motion-est, motion_gt, nan_policy='omit')
