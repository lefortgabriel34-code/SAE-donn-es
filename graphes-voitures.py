import json
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


CAPACITES_STATIONS_VELOS = {
  "Antigone": 239,
  "Arc de Triomphe": 440,
  "Charles de Gaulle": 260,
  "Circe": 1200,
  "Comedie": 664,
  "Corum": 480,
  "Euromedecine": 239,
  "Europa": 591,
  "Foch": 620,
  "Gambetta": 452,
  "Garcia Lorca": 400,
  "Gare": 656,
  "Gaumont EST": 109,
  "Gaumont OUEST": 250,
  "Gaumont-Circe": 500,
  "Mosson": 328,
  "Occitanie": 615,
  "Pitot": 590,
  "Polygone": 1911,
  "Sabines": 285,
  "Sablassou": 379,
  "Saint Jean Le Sec": 285,
  "Triangle": 434,
  "Vicarello": 64
}



DATA_DIR = Path("data-voitures")
OUT_DIR = Path("plots_voitures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SKIP_IF_NO_CAPACITY = True


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M")


def compute_fill_percent(available: float, capacity: float) -> float:
    if capacity <= 0:
        return float("nan")
    fill = ((capacity - available) / capacity) * 100.0
    if fill < 0:
        fill = 0.0
    if fill > 100:
        fill = 100.0
    return fill


def load_timeseries(json_path: Path):
    with json_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    items = []
    for k, v in raw.items():
        try:
            t = parse_dt(k)
            items.append((t, float(v)))
        except Exception:
            continue

    items.sort(key=lambda x: x[0])
    times = [t for t, _ in items]
    values = [v for _, v in items]
    return times, values


def plot_one_station(name: str, times, fill_values):
    fig, ax = plt.subplots()
    ax.plot(times, fill_values)

    ax.set_title(f"Remplissage (%) - {name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Remplissage (%)")
    ax.set_ylim(0, 100)

    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d/%m"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))

    ax.grid(True, which="both", axis="both", linestyle="--", linewidth=0.5, alpha=0.6)
    fig.autofmt_xdate()

    out = OUT_DIR / f"{name}_places_prises_pct.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)



def main():

    json_files = sorted(DATA_DIR.glob("*.json"))

    all_series = {}
    missing_caps = []

    for fp in json_files:
        name = fp.stem
        cap = CAPACITES_STATIONS_VELOS.get(name)

        if cap is None:
            missing_caps.append(name)
            if SKIP_IF_NO_CAPACITY:
                continue
            else:
                cap = 1

        times, values = load_timeseries(fp)
        fill_values = [compute_fill_percent(v, cap) for v in values]

        plot_one_station(name, times, fill_values)
        all_series[name] = (times, fill_values)


    print(f"OK. Graphes exportés dans: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
