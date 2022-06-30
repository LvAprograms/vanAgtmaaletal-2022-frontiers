import numpy as np
import matplotlib.pyplot as plt
import cProfile
import pstats

PTT_FILE_PATH = "C:\\Users\\luukv\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\PAPER\\modelfigs\\PTt\\"
PTT_SAVE_PATH = "C:\\Users\\luukv\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\PAPER\\modelfigs\\PTt\\"


class PTtProf(object):
    """
    object able to parse the file PTt.log for time, coordinates, pressure and time data for a specific marker <ID>
    inputs:
    index: marker ID
    data: file with PTt data
    """

    def __init__(self, index, data):
        # print(index)
        self.i = int(index)
        self.d = data
        self.start_coords = (0, 0)

    def process_data(self):
        """
        function that processes the input data to extract the necessary arrays for PTt path construction
        :return: time, x, y, P, T arrays
        """
        if not ROUGH:
            time = np.round(self.d[:, 1] / 1e6, 2)
        else:
            time = self.d[:, 1]
        x = self.d[:, 2] / 1e3
        y = self.d[:, 3] / 1e3
        self.start_coords = (int(x[0]), int(y[0]))
        pressure = self.d[:, 4] / 1e9
        temperature = self.d[:, 5] - 273.15
        return time, x, y, pressure, temperature

    def plot(self, ax, time_threshold, markers, ax2=None, ax3=None):
        """
        :param ax: axis to plot on
        :param time_threshold: determines how many steps should be plotted (and skips data with too small increments),
        e.g. 1 point per 0.5 MYr. Especially in the startup phase, time slowly progresses.
        :param markers: markers for plotting. Default is given in the :class: PTtProfManager
        :param ax2: optional axis to do experimental plots on (e.g. track not just P and T but also x and y positions
        :param ax3: similar to ax2
        :return: labeltimes (times that were actually used for plotting) and scatter object (sco).
        """
        time, x, y, P, T = self.process_data()
        points = np.arange(0, np.round(max(time), 1), 0.5)
        plotpoints = []
        labeltimes = []
        if not ROUGH:
            loc = 0
            # search algorithm: iterate over idealised time series `points`, minimise difference with actual data points
            # and fill arrays to use for plotting. In this case a while loop is much more convenient than a for loop.
            for i, point in enumerate(points):
                err = 100
                j = loc
                while err > time_threshold and j < len(time):
                    tmp = abs(time[j] - point)
                    if tmp < err:
                        err = tmp  # starting difference between idealised time vector point and actual time data
                        loc = j  # location of minimum difference
                        lab = point  # timestamp of this minimum difference point
                        if loc > 0:
                            plotpoints.append((T[loc], P[loc], x[loc], y[loc]))
                            labeltimes.append(lab)
                    j += 1
        else:
            [plotpoints.append((T[i], P[i], x[i], y[i])) for i in range(len(time))]
            labeltimes = time
        M = markers.pop(0)
        plotpoints = np.array(plotpoints)
        sco = ax.scatter(plotpoints[:, 0], plotpoints[:, 1], marker=M, c=labeltimes, cmap='hot', vmin=0, vmax=115)
        if ax2 is not None and ax3 is not None:
            sco2 = ax2.scatter(plotpoints[:, 2], -plotpoints[:, 3], marker=M, c=labeltimes, cmap='hot', vmin=0, vmax=55)
            sco3 = ax3.scatter(plotpoints[:, 0], -plotpoints[:, 3], marker=M, c=labeltimes, cmap='hot', vmin=0, vmax=55)
            return labeltimes, sco, sco2, sco3
        else:
            return labeltimes, sco


class PTtProfManager(object):
    def __init__(self, file, timethreshold):
        """
        Management class capable of combining indidual marker PTt paths into one PTt figure
        :param file: file containing the PTt data
        :param timethreshold: ideal time interval between two plotted points
        """
        self.MARKERS = ['*', 'd', '^', 'o', 'v', '*', 'd', '^', 'o', 'v']
        self.thresh = timethreshold
        self.f = file

        self.profiles = []
        self.assign_profiles()
        self.plot_ensemble()

    def assign_profiles(self):
        """
        Process data file into different PTtprof classes and combines them in the list self.profiles
        :return: nothing
        """
        markerdata = {}
        with open(self.f) as f:
            # 5 different markers
            for line in f.readlines():
                if not line.startswith("marker"):
                    l = line.split()
                    k = l[0]
                    if k not in list(markerdata.keys()):
                        markerdata[k] = []
                    markerdata[k].append(list([float(l[i]) for i in range(1, len(l))]))

        for marker, data in markerdata.items():
            self.profiles.append(PTtProf(marker, np.array(data)))
        print("Profiles assigned...")

    def plot_ensemble(self):
        """
        Iterates over child PTtProf objects and combines each plot into one ensemble PTt plot.
        :return: nothing
        """
        if BOTTLENECKING:
            prof = cProfile.Profile()
            prof.enable()
        sco = None  # scatter object placeholder
        if EXPERIMENTAL:
            fig, [ax, ax2, ax3] = plt.subplots(nrows=3, ncols=1)
        else:
            fig, ax = plt.subplots()
        plt.xlabel("T [Celsius]")
        plt.ylabel("P [GPa]")
        plt.grid(visible=True)
        # plt.title("PTt path ")
        labels = {}
        for i, profile in enumerate(self.profiles):
            print("Plotting profile {}...".format(i))
            if EXPERIMENTAL:
                labels[profile.start_coords[0]], sco, sco2, sco3 = profile.plot(ax, self.thresh, self.MARKERS, ax2,
                                                                                ax3, )
            else:
                labels[profile.start_coords[0]], sco = profile.plot(ax, self.thresh, self.MARKERS)
        if BOTTLENECKING:
            ps = pstats.Stats(prof)
            ps.sort_stats('calls', 'cumtime')
            ps.print_stats(5)

        plt.legend(labels, loc='upper left')
        # ax.set_xlim([0, 800])
        ax.set_ylim([0.3, 3.6])
        if EXPERIMENTAL:
            ax2.set_xlim([750, 1150])
            ax3.set_xlim([0, 600])
            ax2.set_ylim([-200, 0])
            ax3.set_ylim([-200, 0])

        cb = plt.colorbar(sco)
        cb.set_label("Time [Myr]")
        # ax1.set_title(self.model_id)
        print("Done")


if __name__ == "__main__":
    """
    switches: 
    - ROUGH True means the data are extracted from every 25th prn instead of every timestep during i2elvis
            simulation. Both require different loops to make the data plottable
    - EXPERIMENTAL True means plot not only PTt paths but also x and y position of the markers in separate subplots
    - BOTTLENECKING True uses cProfile module to analyse bottlenecks in the program. Used this to speed up the PTt from
                    minutes to seconds.
    models: list of models to plot the PTt profiles from. 
    """
    ROUGH = True
    EXPERIMENTAL = False
    BOTTLENECKING = False

    models = ["BA", "BE", "BM", "BU", "BW", "BY", "CC", "CD", "CE", "CF", "CG", "CH", "CJ", "CK", "CL", "CM",
              "CO", "CP", "CR", "CU", "CW", "DB", "DC", "DD", "DF", "DG", "DH", "DR", "DT", "DU", "DV", "DZ", "EC",
              "EF", "EG", "EI", "EL", "EM", "EN", "EP", "EQ", "ET", "EX", "FA", "FB", "FD", "FF", "FG", "FH", "FM",
              "FN", "FV", "FY"]
    # models = ["ER", "FI", "FQ"]
    # models = ["FX"]
    # models = ["FP"]
    # models = ["ER", "FI", "FJ", "FK", "FP", "FQ", "FR", "FS", "FT", "FX_fr", "shortpush"]
    for m in models:
        PM = PTtProfManager("{}{}_PTtf.log".format(PTT_FILE_PATH, m), timethreshold=0.001)
        if ROUGH:
            plt.savefig("{}{}_PTt_rough.png".format(PTT_SAVE_PATH, m), dpi=300)
        else:
            plt.savefig("{}{}_PTt.png".format(PTT_SAVE_PATH, m), dpi=300)
