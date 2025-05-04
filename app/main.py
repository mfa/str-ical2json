import datetime

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()


def parse(stream):
    ds = {}
    for line in stream.split("\n"):
        if line.strip() == "BEGIN:VEVENT" and ds:
            if "summary" in ds:
                yield ds
            ds = {}
        if line.startswith("DTSTART"):
            ds["date"] = str(
                datetime.datetime.strptime(
                    line.split(":")[-1].split("T")[0], "%Y%m%d"
                ).date()
            )
        if line.startswith("SUMMARY"):
            ds["summary"] = line.split(":")[-1].strip()


@app.get("/")
@app.post("/")
def ical2json(street: str | None = None, streetnr: str | None = None):
    if not street or not streetnr:
        return {"message": "nothing to see"}

    # valid example:
    # /?street=Rathausplatz&streetnr=1
    r = httpx.get(
        url="https://service.stuttgart.de/lhs-services/aws/api/ical",
        params={"street": street, "streetnr": streetnr},
    )
    if r.status_code == 200:
        return list(sorted(parse(r.text), key=lambda x: x["date"]))
    return HTTPException(status_code=400, detail="Invalid street or street number.")
