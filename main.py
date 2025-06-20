from fastapi import FastAPI
from fastapi.responses import JSONResponse
import bisect
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

saturation_points = [
    (0.05, 0.00105, 30),
    (0.1,  0.00108, 20),
    (0.5,  0.0012,  15),
    (1.0,  0.0016,  8),
    (2.0,  0.0019,  6.5),
    (5.0,  0.0025,  4.5),
    (7.0,  0.0032,  3.2),
    (10.0, 0.0035,  0.0035)
]

pressures = [p[0] for p in saturation_points]
vf_crit = vg_crit = 0.0035

@app.get("/phase-change-diagram")
def get_data(pressure: float):
    print(f"\n📡 Petición recibida - presión: {pressure} MPa")

    # Punto crítico: presión mayor o igual a 10 MPa
    if pressure >= 10.0:
        print("Presión igual o mayor al punto crítico. Devolviendo valores críticos.")
        print(f"vf = {vf_crit}, vg = {vg_crit}")
        return {
            "specific_volume_liquid": vf_crit,
            "specific_volume_vapor": vg_crit
        }

    # Valor exacto en la tabla
    for p, vf, vg in saturation_points:
        if pressure == p:
            print("✅ Valor exacto encontrado en tabla.")
            print(f"➡️ vf = {vf}, vg = {vg}")
            return {
                "specific_volume_liquid": vf,
                "specific_volume_vapor": vg
            }

    # Fuera del rango (menor al mínimo)
    if pressure < pressures[0]:
        print("Presión fuera de rango. Rechazada.")
        return JSONResponse(
            status_code=400,
            content={"error": "Presión fuera de rango (mínimo 0.05 MPa)"}
        )

    # Interpolación
    idx = bisect.bisect_left(pressures, pressure)
    p1, vf1, vg1 = saturation_points[idx - 1]
    p2, vf2, vg2 = saturation_points[idx]

    def interp(x, x1, x2, y1, y2):
        return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

    vf = interp(pressure, p1, p2, vf1, vf2)
    vg = interp(pressure, p1, p2, vg1, vg2)

    print("Interpolación realizada entre:")
    print(f"   P1 = {p1} MPa → vf1 = {vf1}, vg1 = {vg1}")
    print(f"   P2 = {p2} MPa → vf2 = {vf2}, vg2 = {vg2}")
    print(f"Resultado interpolado: vf = {round(vf,6)}, vg = {round(vg,6)}")

    return {
        "specific_volume_liquid": round(vf, 6),
        "specific_volume_vapor": round(vg, 6)
    }
