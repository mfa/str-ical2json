import datetime

import httpx
from fastmcp import FastMCP

mcp = FastMCP(
    name="ical2json Stuttgart",
    instructions="This server provides the next waste retrieval dates for the city of Stuttgart as json.",
)


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


@mcp.tool(
    name="stuttgart_ical2json",
    description="Stuttgart waste dates",
    annotations={"readOnlyHint": True, "openWorldHint": False},
)
async def ical2json(street: str, streetnr: str):
    # valid example:
    # street=Rathausplatz
    # streetnr=1
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url="https://service.stuttgart.de/lhs-services/aws/api/ical",
            params={"street": street, "streetnr": streetnr},
        )
        if r.status_code == 200:
            return list(sorted(parse(r.text), key=lambda x: x["date"]))
    raise ValueError("Invalid street or street number.")


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
    )
