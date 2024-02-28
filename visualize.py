import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


def scatter(motion_est, motion_gt):
    # Perform linear regression
    slope, intercept, _, _, _ = stats.linregress(motion_est, motion_gt)
    line = slope * motion_est + intercept

    # Create a scatter plot with a fitted line
    plt.scatter(motion_est, motion_gt, label='Data')
    plt.plot(motion_est, line, color='red', label=f'Fit: y={slope:.2f}x+{intercept:.2f}')

    # Adding titles, labels, and legend
    plt.xlabel("Motion Estimate")
    plt.ylabel("Motion GT")
    plt.legend()

    # Show plot with grid
    plt.grid(True)
    plt.show()


def ranking(motion_est, motion_gt)
    # Sort both arrays based on motion_est
    indices_sorted_by_motion = np.argsort(motion_est)
    sorted_gt = motion_gt[indices_sorted_by_motion]

    # Apply percentile-based normalization
    low_percentile = np.percentile(sorted_gt, 25)
    high_percentile = np.percentile(sorted_gt, 75)
    normalized_gt = (sorted_opt_flows - low_percentile) / (high_percentile - low_percentile)
    # Clip values to [0, 1] to ensure they fall within the colormap range
    normalized_gt = np.clip(normalized_opt_flows, 0, 1)

    # Create a colormap from blue to red
    colormap = plt.cm.get_cmap('coolwarm')

    # Generate colors for each cell based on optical flow scores
    cell_colors = colormap(normalized_gt)

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(2, 10))  # Adjust size as needed
    for i, color in enumerate(cell_colors):
        ax.add_patch(plt.Rectangle((0, i), 1, 1, color=color))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(motion_est))
    ax.set_yticks(np.arange(len(motion_est)) + 0.5)
    ax.set_yticklabels(indices_sorted_by_motion + 1)  # +1 to start ranking from 1
    ax.set_xticks([])
    ax.invert_yaxis()  # Invert y-axis so that rank 1 is at the top
    ax.set_title('Video Ranking by Estimated Motion\nColored by Optical Flow (Balanced)')
    plt.tight_layout()
    plt.show()
