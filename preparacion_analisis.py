# Proyecto final - Ingeniería Civil
# Ejecute desde la carpeta raíz: python codigo/preparacion_analisis.py
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "datos" / "dataset_original.csv")
for col in ["fecha_inicio_proyecto", "fecha_corte", "fecha_fin_planeada"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

missing_cols = ["costo_real_periodo_cop", "avance_real_pct_acum",
                "consumo_combustible_l", "emisiones_co2_kg",
                "material_reciclado_pct"]
for col in missing_cols:
    df[col + "_faltante"] = df[col].isna().astype(int)
    df[col] = df[col].fillna(df[col].median())

df["desviacion_costo_cop"] = df.costo_real_periodo_cop - df.costo_planeado_periodo_cop
df["sobrecosto_pct"] = np.where(df.costo_planeado_periodo_cop.ne(0),
    df.desviacion_costo_cop / df.costo_planeado_periodo_cop * 100, np.nan)
df["desviacion_avance_pp"] = df.avance_real_pct_acum - df.avance_planeado_pct_acum
df["desviacion_maquinaria_h"] = df.horas_maquinaria_reales - df.horas_maquinaria_planeadas
df["combustible_por_hora"] = df.consumo_combustible_l / df.horas_maquinaria_reales.replace(0, np.nan)
df["emisiones_por_hora"] = df.emisiones_co2_kg / df.horas_maquinaria_reales.replace(0, np.nan)
df["mes_corte"] = df.fecha_corte.dt.to_period("M").astype(str)

for col in ["costo_real_periodo_cop", "horas_maquinaria_reales",
            "precipitacion_mm", "incidentes_seguridad"]:
    q1, q3 = df[col].quantile([.25, .75])
    iqr = q3 - q1
    df[col + "_atipico_iqr"] = ((df[col] < q1 - 1.5*iqr) |
                                  (df[col] > q3 + 1.5*iqr)).astype(int)

df.to_csv(ROOT / "datos" / "dataset_procesado.csv", index=False)
valid = pd.read_csv(ROOT / "datos" / "dataset_original.csv")
valid = valid[["costo_planeado_periodo_cop", "costo_real_periodo_cop"]].dropna()
p = valid.costo_planeado_periodo_cop.to_numpy()
r = valid.costo_real_periodo_cop.to_numpy()
print("Registros:", len(df), "Proyectos:", df.proyecto_id.nunique())
print("Error absoluto promedio inicial:", np.mean(np.abs(r-p)))
for factor in [0.95, 1.00, 1.05, 1.10]:
    print(f"Factor {factor:.2f}: EAP = {np.mean(np.abs(r-p*factor)):,.0f} COP")
print("Archivo procesado guardado.")
