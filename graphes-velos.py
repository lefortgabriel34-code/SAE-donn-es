import json
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


CAPACITES_STATIONS_VELOS = {
  "Aiguelongue": 7,
  "Albert 1er - Cathédrale": 12,
  "Antigone centre": 12,
  "Beaux-Arts": 15,
  "Boutonnet": 13,
  "Celleneuve": 8,
  "Charles Flahault": 8,
  "Cité Mion": 7,
  "Comedie Baudin": 8,
  "Comédie": 18,
  "Corum": 12,
  "Deux Ponts - Gare Saint-Roch": 8,
  "Emile Combes": 8,
  "Euromédecine": 8,
  "Fac de Lettres": 12,
  "FacdesSciences": 24,
  "Foch": 4,
  "Gambetta": 8,
  "Garcia Lorca": 8,
  "Halles Castellane": 12,
  "Hôtel de Ville": 16,
  "Hôtel du Département": 8,
  "Jardin de la Lironde": 8,
  "Jean de Beins": 16,
  "Jeu de Mail des Abbés": 8,
  "Les Arceaux": 8,
  "Les Aubes": 8,
  "Louis Blanc": 16,
  "Malbosc": 8,
  "Marie Caizergues": 8,
  "Médiathèque Emile Zola": 16,
  "Nombre d Or": 16,
  "Nouveau Saint-Roch": 8,
  "Observatoire": 7,
  "Occitanie": 32,
  "Odysseum": 8,
  "Parvis Jules Ferry - Gare Saint-Roch": 8,
  "Place Albert 1er - St Charles": 27,
  "Place Viala": 8,
  "Plan Cabanes": 12,
  "Pont de Lattes - Gare Saint-Roch": 12,
  "Port Marianne": 16,
  "Providence - Ovalie": 8,
  "Prés d Arènes": 8,
  "Père Soulas": 8,
  "Pérols Etang de l Or": 68,
  "Renouvier": 8,
  "Richter": 16,
  "Rondelet": 16,
  "Rue Jules Ferry - Gare Saint-Roch": 12,
  "Sabines": 8,
  "Saint-Denis": 8,
  "Saint-Guilhem - Courreau": 8,
  "Sud De France": 6,
  "Tonnelles": 8,
  "Vert Bois": 16,
  "Voltaire": 8
}



DATA_DIR = Path("data-velos")
OUT_DIR = Path("./plots_velos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SKIP_IF_NO_CAPACITY = True


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M")


def compute_fill_percent(available: float, capacity: float) -> float:
    fill = (available / capacity) * 100.0
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

    ax.set_title(f"Vélos disponibles (%) - {name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Disponibilité vélos (%)")
    ax.set_ylim(0, 100)

    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d/%m"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))

    ax.grid(True, which="both", axis="both", linestyle="--", linewidth=0.5, alpha=0.6)
    fig.autofmt_xdate()

    out = OUT_DIR / f"{name}_velos_dispo_pct.png"
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
