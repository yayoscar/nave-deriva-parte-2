from fastapi import FastAPI
from fastapi.responses import JSONResponse
import bisect

app = FastAPI()

# Tabla más precisa basada en comportamiento físico estimado
saturation_points = [
    (0.05, 0.001050, 30.000000),
    (0.1,  0.001080, 20.000000),
    (0.5,  0.001200, 15.000000),
    (1.0,  0.001600, 8.000000),
    (2.0,  0.001900, 6.500000),
    (3.0,  0.002200, 5.500000),
    (4.0,  0.002400, 5.000000),
    (5.0,  0.002500, 4.500000),
    (6.0,  0.002900, 4.000000),
    (7.0,  0.003200, 3.200000),
    (8.0,  0.003350, 2.100000),
    (9.0,  0.003450, 1.100000),
    (10.0, 0.003500, 0.003500)  # Punto crítico
]

pressures = [p[0] for p in saturation_points]
vf_crit = vg_crit = 0.0035

@app.get("/phase-change-diagram")
def get_data(pressure: float):
    print(f"\n📡 Petición recibida - presión: {pressure} MPa")

    if pressure >= 10.0:
        print("⚠️ Presión igual o mayor al punto crítico. Devolviendo valores críticos.")
        print(f"✅ vf = {vf_crit}, vg = {vg_crit}")
        return {
            "specific_volume_liquid": vf_crit,
            "specific_volume_vapor": vg_crit
        }

    for p, vf, vg in saturation_points:
        if pressure == p:
            print("✅ Valor exacto encontrado en tabla.")
            print(f"➡️ vf = {vf}, vg = {vg}")
            return {
                "specific_volume_liquid": vf,
                "specific_volume_vapor": vg
            }

    if pressure < pressures[0]:
        print("❌ Presión fuera de rango. Rechazada.")
        return JSONResponse(
            status_code=400,
            content={"error": "Presión fuera de rango (mínimo 0.05 MPa)"}
        )

    idx = bisect.bisect_left(pressures, pressure)
    p1, vf1, vg1 = saturation_points[idx - 1]
    p2, vf2, vg2 = saturation_points[idx]

    def interp(x, x1, x2, y1, y2):
        return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

    vf = float("{:.6f}".format(interp(pressure, p1, p2, vf1, vf2)))
    vg = float("{:.6f}".format(interp(pressure, p1, p2, vg1, vg2)))

    print("🔄 Interpolación realizada entre:")
    print(f"   P1 = {p1} MPa → vf1 = {vf1}, vg1 = {vg1}")
    print(f"   P2 = {p2} MPa → vf2 = {vf2}, vg2 = {vg2}")
    print(f"➡️ Resultado interpolado: vf = {vf}, vg = {vg}")

    return {
        "specific_volume_liquid": vf,
        "specific_volume_vapor": vg
    }
