from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
from numpy import array, amax, amin
from plot_slabpull import plot_slab_pull_data
from matplotlib.ticker import MultipleLocator

BASE_PATH = "C:\\Users\\luukv\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\PAPER\\REVIEW_round1\\forcedata_accurate\\"
# BASE_PATH = "C:\\Users\\luukv\\Documents\\ThesisData\\"
SAVE_PATH = "C:\\Users\luukv\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\PAPER\\REVIEW_round1\\ExtraFigs\\"


def split_pos_neg_values(x, y, slab_pull=False):
    """
    Splits lists or array y into positive and negative values.
    :param x: assumes this is the time vector
    :param y: assumes this is the force (+/-)
    :param slab_pull: flag to distinguish slab pull from mantle drag data (which are treated differently)
    :return: lists of positive and negative indices.
    """
    pos_id = []
    neg_id = []
    for j in range(len(x)):
        if not slab_pull:
            cmp = sum(y[j]) / len(y[j])  # average the mantle drag, because each y[j] contains values of 4 depths
        else:
            cmp = y[j]
        if cmp > 0.1:  # values of zero are ignored, because that means no force was calculated.
            pos_id.append(j)
        elif cmp < -0.1:
            neg_id.append(j)
        else:
            # print("value at t={} (y={}) is not taken into account".format(x[j], y[j]))
            pass
    return pos_id, neg_id


def segmentise(pos_id, neg_id):
    pos_segments = {0: []}
    neg_segments = {0: []}
    cur_seg = 0
    increments = []
    for i in range(1, len(pos_id)):
        increment = pos_id[i] - pos_id[i-1]
        increments.append(increment)
        if increment != 1:
            cur_seg += 1
            pos_segments[cur_seg] = []
        pos_segments[cur_seg].append(pos_id[i])
    cur_seg = 0
    for i in range(1, len(neg_id)):
        increment = neg_id[i] - neg_id[i-1]
        increments.append(increment)
        if increment != 1:
            cur_seg += 1
            neg_segments[cur_seg] = []
        neg_segments[cur_seg].append(neg_id[i])
    return pos_segments, neg_segments


class SignSwitchingLogPlotter(object):
    """
    Class that generates and manages two subplots, the upper for positive values and the lower for negative values.
    It also contains functions for splitting data in positive and negative values, splitting those into segments which
    can then be plotted as line segments. For mantle drag it generates "error areas".
    """
    def __init__(self):
        """
        self.lines: lines to be placed in the legend to avoid items occurring more than once
        sets up the figure and axis properties
        """
        self.lines = [Line2D([0], [0], color=(0, 0.5, 0.1), lw=1),
                      Line2D([0], [0], color=(0, 0.5, 0.1, 0.4), lw=1),
                      Line2D([0], [0], color=(0, 0.75, 0.15, 0.4), lw=1),
                      Line2D([0], [0], color=(0, 0.1, 0.5), lw=2)]
        self.fig, self.ax = plt.subplots(2, figsize=(8, 3.5))
        self.plot_labels = []
        self.ax[0].set_ylabel(r'$F > 0$' + " [N/m]")
        self.ax[1].set_ylabel(r'$F < 0$' + " [N/m]")
        # font = {'family': 'default',
        #         'weight': 'normal',
        #         'size': 14}
        for axis in self.ax:
            # axis.grid(b=True)
            axis.set_xlabel("Time [Myr]")
            axis.set_xlim([0, 60])
            axis.xaxis.set_major_locator(MultipleLocator(10))
            axis.xaxis.set_major_formatter('{x:.0f}')
            # For the minor ticks, use no labels; default NullFormatter.
            axis.xaxis.set_minor_locator(MultipleLocator(5))
            axis.set_yticks([1e12, 1e14])
            # plt.rc('font', **font)
            # plt.rc('xtick', labelsize=18)
            # plt.rc('ytick', labelsize=18)

    def plot(self, xdata, ydata, file=None, slab_pull=False):
        plot_label = file.capitalize() + " mantle drag" if not slab_pull else "Slab pull"
        pos_id, neg_id = split_pos_neg_values(xdata, ydata, slab_pull)
        pos_segments, neg_segments = segmentise(pos_id, neg_id)
        self.plot_labels.append(plot_label) if plot_label not in self.plot_labels else None
        clr = (0, 0.1, 0.5) if slab_pull else (0, 0.5, 0.1)
        lns = '-'
        for segment, ids in pos_segments.items():
            if not slab_pull:
                mx = amax(ydata[ids], 1)
                mn = amin(ydata[ids], 1)
                self.ax[0].fill_between(xdata[ids], mx, mn, color=clr, linestyle=lns, linewidth=1)
            else:
                self.ax[0].plot(xdata[ids], ydata[ids], color=clr, linestyle=lns, linewidth=2)
        for segment, ids in neg_segments.items():
            if not slab_pull:
                mx = amax(-ydata[ids], 1)
                mn = amin(-ydata[ids], 1)
                self.ax[1].fill_between(xdata[ids], mx, mn, color=clr, linestyle=lns, linewidth=1)
            else:
                self.ax[1].plot(xdata[ids], -ydata[ids], color=clr, linestyle=lns, linewidth=2)
        self.ax[0].set_ylim([1e9, 8e15])
        self.ax[1].set_ylim([8e15, 1e9])

        self.ax[0].set_yscale('log')
        self.ax[1].set_yscale('log')
        plt.subplots_adjust(bottom=0.15, hspace=0.2)

    def save_fig(self, model):
        if ONLY_MEAN:
            self.fig.legend([self.lines[0], self.lines[-1]], self.plot_labels, ncol=5, loc='lower left',
                            bbox_to_anchor=(0.16, 0.9, 0.5, 0.5), prop={'size': 8})
        else:
            self.fig.legend(self.lines, self.plot_labels, ncol=5,  loc='lower left',
                        bbox_to_anchor=(0.16, 0.9, 0.5, 0.5), prop={'size': 8})
        if ONLY_MEAN:
            self.fig.savefig("{}{}_forces_only_mean_nogrid.png".format(SAVE_PATH, model), dpi=300)
        else:
            self.fig.savefig("{}{}_forces_nogrid.png".format(SAVE_PATH, model), dpi=300)
        plt.close(self.fig)

    def add_error_areas(self, x, y, f):
        pos_id, neg_id = split_pos_neg_values(x, y, slab_pull=False)
        pos_segments, neg_segments = segmentise(pos_id, neg_id)
        clr = (0, 0.5, 0.1, 0.4) if f == "max" else (0, 0.75, 0.15, 0.4)
        for segment, ids in pos_segments.items():
            mx = amax(y[ids], 1)
            mn = amin(y[ids], 1)
            self.ax[0].fill_between(x[ids], mx, mn, color=clr, linestyle='-', linewidth=1)
        for segment, ids in neg_segments.items():
            mx = amax(-y[ids], 1)
            mn = amin(-y[ids], 1)
            self.ax[1].fill_between(x[ids], mx, mn, color=clr, linestyle='-', linewidth=1)
        self.plot_labels.append(f.capitalize() + " mantle drag")


class ForcePlotter(object):
    def __init__(self, model_list: list, files: list):
        self.models = model_list
        self.data = {}
        self.time = {}
        self.files = files

    def read_data(self, model: str, file: str):
        self.data[model] = {}
        self.time[model] = {}
        self.data[model][file] = []
        self.time[model][file] = []
        self.data[model]["xUP_start"] = []
        with open(BASE_PATH + '{}_MDdata_{}.txt'.format(model, file)) as f:
            for line in f.readlines():
                line = line.split()
                self.time[model][file].append(float(line[0]) / 1e6)
                self.data[model][file].append([float(line[k]) for k in range(3, 7)])
                self.data[model]["xUP_start"].append(float(line[1]) / 1e3)

    def process_and_plot_data(self, plot_ratio=False, plot_xOP_start=False):
        peak_slab_pull = []
        for m in self.models:
            print("Plotting forces for model {}".format(m))
            fig2, ax2 = plt.subplots()
            log_plotter = SignSwitchingLogPlotter()
            t, slab_pull, slab_area = plot_slab_pull_data(m, overlay=True)
            peak_slab_pull.append([max(slab_pull), t[slab_pull.argmin()]])
            for f in self.files:
                self.read_data(m, f)
                if f == "mean":
                    log_plotter.plot(xdata=array(self.time[m][f]), ydata=array(self.data[m][f]), file=f)
                    if plot_ratio:
                        ratio = []
                        rtime = []
                        for i in range(len(slab_pull)):
                            if sum(self.data[m][f][i]) > 0 or sum(self.data[m][f][i]) < 0:
                                rtime.append(t[i])
                                ratio.append(abs(slab_pull[i] / (sum(self.data[m][f][i]) / len(self.data[m][f][i]))))
                        ax2.semilogy(rtime, ratio, marker='o', color="black", markerfacecolor='black')
                        ax2.set_xlabel("Time [Myr]")
                        ax2.set_ylim([0.01, 50000])
                        ax2.set_xlim([0, 60]) if m != "FX_rerun" else ax2.set_xlim([1, 115])
                        ax2.set_ylabel(r'$F_{SP}/F_{MD}$')
                        fig2.savefig("{}force_ratio{}.png".format(SAVE_PATH, m), dpi=300)
                        plt.close(fig2)
                else:
                    log_plotter.add_error_areas(array(self.time[m][f]), y=array(self.data[m][f]), f=f)
            log_plotter.plot(xdata=array(t), ydata=array(slab_pull), slab_pull=True)
            log_plotter.save_fig(m)

        with open("{}peak_slab_pull.txt".format(SAVE_PATH), 'w') as f:
            for item in peak_slab_pull:
                f.write("{}\t{}\n".format(item[1], item[0]))
                
        # Added during revision, 23-6-2022: plot xUP_start evolution with time if needed
        if plot_xOP_start:
            for m in self.models:
                fig3, ax3 = plt.subplots()
                ax3.plot(self.time[m]["max"][7:-1], self.data[m]["xUP_start"][7:-1], 'k*--')
                ax3.set_xlim([1, 56]) if m != "FX_rerun" else ax3.set_xlim([1, 115])
                ax3.set_xlabel("Time [Myr]")
                ax3.set_ylabel(r'$x_{OPstart}$ [km]')
                plt.savefig("{}xUP_start_{}.png".format(SAVE_PATH, m), dpi=300)
                plt.close(fig3)


if __name__ == "__main__":
    """
    Usage of script: 
    1) change the `BASE_PATH` and `SAVE_PATH` variables to where your force data are stored and where you want
       to store the figures
    2) write the model_id names in a list as below
    3) run the script
    """
    ONLY_MEAN = True
    # models = ["reflong", "reffree", "ref5cm"]
    # models = ["ER", "FP_rerun", "FX_p1_rerun", "FX_p2_rerun"]
    # models = ["FX_rerun"]
    # models = ["FI_shortpush"]
    models = ["ER_rerun", "FI_rerun", "FJ_rerun", "FK_rerun", "FP_rerun", "FQ_rerun", "FR_rerun", "FS_rerun",
              "FT_rerun", "FX_rerun", "reflong", "reffree", "ref5cm", "refcold", "refcolder", "refcoldest", "thineur"]
    FP = ForcePlotter(models, files=["mean"]) if ONLY_MEAN else ForcePlotter(models, files=["mean", "min", "max"])
    FP.process_and_plot_data(plot_ratio=True, plot_xOP_start=False)
