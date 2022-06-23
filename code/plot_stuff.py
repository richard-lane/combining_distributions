"""
Plot stuff from CSV files dumped by the C++ generating script

"""
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process


def plot_pdf(name: str) -> None:
    """
    Plot PDFs from files named f"vals_{name}.csv" and f"domain_{name}.csv"

    """
    x = np.genfromtxt(f"domain_{name}.csv", delimiter=",")
    y = np.genfromtxt(f"vals_{name}.csv", delimiter=",")

    fig, ax = plt.subplots()

    ax.plot(x, y)
    ax.set_title(name)

    fig.savefig(f"{name}.png")


def plot_reco() -> None:
    """
    Plot reco samples on a histogram

    """
    fig, ax = plt.subplots()
    f = np.genfromtxt("fsamples.csv", delimiter=",")
    g = np.genfromtxt("gsamples.csv", delimiter=",")

    kw = {"bins": np.linspace(-2, 6, 50), "histtype": "step"}

    ax.hist(f, **kw)
    ax.hist(g, **kw)
    ax.hist(np.concatenate((f, g)), **kw)

    fig.savefig("recoSamples.png")


def plot_approx() -> None:
    """
    Plot samples from the approximate generating PDF on a histogram

    """
    fig, ax = plt.subplots()
    a = np.genfromtxt("approxsamples.csv", delimiter=",")

    kw = {"bins": np.linspace(-2, 6, 50), "histtype": "step"}

    ax.hist(a, **kw)

    f = np.genfromtxt("fsamples.csv", delimiter=",")
    g = np.genfromtxt("gsamples.csv", delimiter=",")
    ax.hist(np.concatenate((f, g)), **kw, label="reco")

    fig.savefig("approxSamples.png")


def plot_efficiency() -> None:
    """
    Plot the efficiency we measure and the true efficiency

    """
    fig, ax = plt.subplots()
    x = np.genfromtxt("domain_efficiency.csv", delimiter=",")
    y = np.genfromtxt("vals_efficiency.csv", delimiter=",")

    # Scale the efficiency to have a mean of 1
    y /= np.mean(y[~np.isnan(y)])

    ax.plot(x, y, "k", label="true")

    bins = np.linspace(-2, 6, 50)

    f = np.genfromtxt("fsamples.csv", delimiter=",")
    g = np.genfromtxt("gsamples.csv", delimiter=",")
    true_count, _ = np.histogram(np.concatenate((f, g)), bins)

    approx_count, _ = np.histogram(
        np.genfromtxt("approxsamples.csv", delimiter=","), bins
    )

    e = true_count / approx_count
    err = e * np.sqrt(1 / true_count + 1 / approx_count)

    scale = np.mean(e)
    err /= scale
    e /= scale

    centres = (bins[1:] + bins[:-1]) / 2
    ax.errorbar(centres, e, yerr=err, fmt="r.", label="measured")

    ax.legend()

    fig.savefig(f"measured_efficiency.png")


def main() -> None:
    procs = [
        Process(target=plot_pdf, args=(s,)) for s in ("f", "g", "efficiency", "approx")
    ]
    procs += [Process(target=f) for f in (plot_reco, plot_approx, plot_efficiency)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()


if __name__ == "__main__":
    main()
