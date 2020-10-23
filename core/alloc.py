#!/usr/bin/env python3

from pathlib import Path
from types import SimpleNamespace
import click

HERE = Path(__file__).parent.resolve()

def parse_alloc_data(alloc_data):
    parsed_data = {}
    for line in alloc_data:
        ident, allocs, calls = line.strip().split(" ")
        allocs = int(allocs)
        calls = int(calls)
        filename, lineno = ident.split(":")
        lineno = int(lineno)

        filedata = parsed_data.setdefault(filename, {})
        filedata[lineno] = {
            "total_allocs": allocs,
            "total_calls": calls,
            "avg_allocs": allocs / calls,
        }
    return parsed_data


@click.group()
@click.pass_context
@click.option("-a", "--alloc-data", type=click.File(), default="src/alloc_data.txt")
@click.option("-t", "--type", type=click.Choice(("total", "avg")), default="avg")
def cli(ctx, alloc_data, type):
    ctx.obj = SimpleNamespace(data=parse_alloc_data(alloc_data), type=type)


def _normalize_filename(filename):
    if filename.startswith("src/"):
        return filename[4:]
    return filename


@cli.command()
@click.pass_obj
@click.argument("filename")
def annotate(obj, filename):
    filename = _normalize_filename(filename)

    if obj.type == "total":
        alloc_str = lambda line: str(line["total_allocs"])
    else:
        alloc_str = lambda line: "{:.2f}".format(line["avg_allocs"])

    filedata = obj.data[filename]

    linedata = {lineno: alloc_str(line) for lineno, line in filedata.items()}
    maxlen = max(len(l) for l in linedata.values())

    lineno = 0
    for line in open("src/" + filename):
        lineno += 1
        linecount = linedata.get(lineno, "")
        print(f"{linecount:>{maxlen}}  {line}", end="")


def _list(obj, field, reverse):
    file_sums = {
        filename: sum(line[field] for line in lines.values())
        for filename, lines in obj.data.items()
    }

    return sorted(
        file_sums.items(), key=lambda x: x[1], reverse=reverse
    )

@cli.command()
@click.pass_obj
@click.option("-r", "--reverse", is_flag=True)
def list(obj, reverse):
    if obj.type == "total":
        field = "total_allocs"
        field_fmt = "{}"
    else:
        field = "avg_allocs"
        field_fmt = "{:.2f}"

    file_sums = _list(obj, field, reverse)

    maxlen = max(len(field_fmt.format(l[1])) for l in file_sums)
    for filename, file_sum in file_sums:
        num_str = field_fmt.format(file_sum)
        print(f"{num_str:>{maxlen}}  {filename}")


@cli.command()
@click.pass_obj
@click.option("-r", "--reverse", is_flag=True)
@click.argument("htmldir")
def html(obj, reverse, htmldir):
    file_sums = _list(obj, "total_allocs", reverse)  #FIXME total

    maxlen = 6
    with open(f"{htmldir}/index.html", "w") as f:
        f.write("<html><tt>")
        for filename, file_sum in file_sums:
            f.write(f"{file_sum:>{maxlen}}  <a href='{filename}.html'>{filename}</a><br>")
        f.write("</tt></html>")

    for filename in file_sums:
        filename = _normalize_filename(filename[0])
        htmlfile = Path(htmldir) / filename
        htmlfile.parent.mkdir(parents=True, exist_ok=True)

        with open(str(htmlfile) + ".html", "w") as f:
            filedata = obj.data[filename]
            f.write(f"<html><title>{filename}</title><tt><table>")
            f.write(f"<tr>")
            f.write(f"<td style='color: grey'><tt>#</tt></td>")
            f.write("<td style='text-align: right'><tt>avg</tt></td>")
            f.write("<td style='text-align: right'><tt>total</tt></td>")
            f.write("<td></td>")
            f.write("</tr>")
            lineno = 0
            for line in open(HERE / "src" / filename):
                line = line.rstrip("\n").replace(" ", "&nbsp;")
                lineno += 1
                total = filedata.get(lineno, {}).get("total_allocs", 0)
                avg = filedata.get(lineno, {}).get("avg_allocs", 0)
                f.write("<tr>")
                f.write(f"<td style='color: grey'><tt>{lineno}</tt></td>")
                f.write(f"<td style='text-align: right'><tt>{avg:.2f}</tt></td>")
                f.write(f"<td style='text-align: right'><tt>{total}</tt></td>")
                f.write(f"<td><tt>{line}</tt></td>")
                f.write("</tr>")
            f.write("</table></tt></html>")


if __name__ == "__main__":
    cli()
