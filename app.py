import os
from datetime import date
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras

app = Flask(__name__)
CORS(app) 

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

FILES_DIR = os.getenv("FILES_DIR", "/files/movimientos_fotos")
PUBLIC_FILES_PREFIX = os.getenv("PUBLIC_FILES_PREFIX", "/files")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )

def moneda_to_text(moneda_code: int) -> str:
    return "Soles" if moneda_code == 1 else "Dólares" if moneda_code == 2 else "Desconocida"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/egresos")
def egresos():
    categoria = request.args.get("categoria")
    para_quien = request.args.get("para_quien")
    metodo = request.args.get("meotodo")
    pagado = request.args.get("pagado")

    limit = int(request.args.get("limit", "30"))
    offset = int(request.args.get("offset", "0"))

    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200
    if offset < 0:
        offset = 0

    where = []
    params = {}

    if categoria:
        where.append("categoria = %(categoria)s")
        params["categoria"] = categoria
    if para_quien:
        where.append("para_quien = %(para_quien)s")
        params["para_quien"] = para_quien
    if pagado in ("0", "1"):
        where.append("esta_pagado = %(pagado)s")
        params["pagado"] = int(pagado)
    if metodo:
        where.append("metodo_pago = %(metodo)s")
        params["metodo"] = metodo

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    # 1) total para paginación
    count_sql = f"SELECT COUNT(*) AS total FROM movimientos {where_sql};"

    # 2) items paginados
    data_sql = f"""
        SELECT
            id, fecha_movimiento, moneda, monto, categoria, descripcion,
            metodo_pago, para_quien, esta_pagado, foto_path, created_at
        FROM movimientos
        {where_sql}
        ORDER BY fecha_movimiento DESC, created_at DESC
        LIMIT %(limit)s OFFSET %(offset)s;
    """

    params_data = dict(params)
    params_data["limit"] = limit
    params_data["offset"] = offset

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(count_sql, params)
            total = cur.fetchone()["total"]

            cur.execute(data_sql, params_data)
            rows = cur.fetchall()

    items = []
    for r in rows:
        foto_url = None
        if r.get("foto_path"):
            filename = os.path.basename(r["foto_path"])
            foto_url = f"{PUBLIC_FILES_PREFIX}/{filename}"

        items.append({
            "id": r["id"],
            "fecha_movimiento": r["fecha_movimiento"].isoformat() if isinstance(r["fecha_movimiento"], date) else r["fecha_movimiento"],
            "moneda": int(r["moneda"]),
            "monto": float(r["monto"]),
            "categoria": r["categoria"],
            "descripcion": r["descripcion"],
            "metodo_pago": r["metodo_pago"],
            "para_quien": r["para_quien"],
            "esta_pagado": int(r["esta_pagado"]),
            "foto_url": foto_url,
            "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
        })

    return jsonify({
        "items": items,
        "paging": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (offset + limit) < total
        }
    })

@app.patch("/api/movimientos/<int:mov_id>/pago")
def marcar_pago(mov_id: int):
    """
    Body JSON:
      { "esta_pagado": 0|1 }
    """
    body = request.get_json(silent=True) or {}
    if "esta_pagado" not in body:
        return {"error": "Falta 'esta_pagado' (0 o 1)."}, 400

    try:
        value = int(body["esta_pagado"])
    except Exception:
        return {"error": "'esta_pagado' debe ser 0 o 1."}, 400

    if value not in (0, 1):
        return {"error": "'esta_pagado' debe ser 0 o 1."}, 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE movimientos SET esta_pagado = %s WHERE id = %s RETURNING id;",
                (value, mov_id),
            )
            row = cur.fetchone()
            if not row:
                return {"error": "No existe ese movimiento."}, 404

    return {"id": mov_id, "esta_pagado": value}

@app.get("/files/<path:filename>")
def serve_file(filename: str):
    """
    Sirve imágenes guardadas por n8n desde la carpeta montada.
    """
    return send_from_directory(FILES_DIR, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
