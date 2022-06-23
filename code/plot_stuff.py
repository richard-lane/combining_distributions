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
    mean = np.mean(y[~np.isnan(y)])

    print(y)

    ax.plot(x, y, label="true")

    bins = np.linspace(-2, 6, 50)

    f = np.genfromtxt("fsamples.csv", delimiter=",")
    g = np.genfromtxt("gsamples.csv", delimiter=",")
    true_count, _ = np.histogram(np.concatenate((f, g)), bins)

    approx_count, _ = np.histogram(
        np.genfromtxt("approxsamples.csv", delimiter=","), bins
    )

    e = true_count / approx_count
    e /= np.mean(e)
    e *= mean
    centres = (bins[1:] + bins[:-1]) / 2
    ax.plot(centres, e, label="measured")

    ax.legend()

    fig.savefig(f"measured_efficiency.png")


def main() -> None:
    procs = [
        Process(target=plot_pdf, args=(s,)) for s in ("f", "g", "efficiency", "approx")
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    plot_reco()
    plot_approx()

    plot_efficiency()


if __name__ == "__main__":
    main()
