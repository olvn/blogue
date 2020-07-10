import click
from pathlib import Path
from jinja2 import Template
from bs4 import BeautifulSoup
from datetime import datetime
from shutil import copy


@click.group()
def cli():
    pass


@click.command()
@click.argument("name")
def create(name):
    """creates blog"""
    Path.mkdir(Path.cwd() / name)
    Path.mkdir(Path.cwd() / name / "build", parents=True)
    Path.mkdir(Path.cwd() / name / "build" / "posts", parents=True)

    with open(Path.cwd() / name / "index.j2", "w") as f:
        f.write(index_template(name))

    click.echo(f"Created blog '{name}'")


@click.command()
def build():
    """builds blog"""
    posts = sorted(
        [parse_post(post) for post in list_posts()],
        key=lambda k: k["date"],
        reverse=True,
    )

    with open(Path.cwd() / "index.j2", "r") as f:
        index = f.read()

    processed_index = Template(index).render(posts=posts)

    with open(Path.cwd() / "build" / "index.html", "w") as f:
        f.write(processed_index)

    click.echo(f"Built blog")


@click.command()
@click.option("--title")
def post(title):
    """creates post"""
    if not title:
        title = datetime.now().strftime("%d%m%Y_%H%M%S")
    with open(Path.cwd() / "build" / "posts" / f"{title}.html", "w") as post:
        post.write(post_template(title))

    click.echo(f'Created post "{title}"')


@click.command()
def eject():
    """places blogue script in working directory for user modification"""
    copy(__file__, Path.cwd() / "blogue.py")
    click.echo(f"ejected blogue - have fun!")


def parse_post(post_path):
    url = Path("posts") / post_path.name
    with open(post_path, "r") as post_file:
        post_html = post_file.read()
        post_soup = BeautifulSoup(post_html, "html.parser")
        title = post_soup.find("meta", property="blogue:title")["content"]
        date_str = post_soup.find("meta", property="blogue:date")["content"]
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    return {"url": url, "title": title, "date": date}


def list_posts():
    return list((Path.cwd() / "build" / "posts").glob("*.html"))


def index_template(name):
    return f"""<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8">
		<title>{name}</title>
	</head>
	<body>
        <ul>
            {{% for post in posts %}}
                <li>{{{{post.date.strftime("%Y-%m-%d")}}}} <a href="{{{{ post.url }}}}">{{{{ post.title }}}}</a></li>
            {{% endfor %}}
        </ul>
	</body>
</html>"""


def post_template(title):
    return f"""<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8">
        <meta property="blogue:title" content="{title}">
        <meta property="blogue:date" content="{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}">
		<title>{title}</title>
	</head>
	<body>
	</body>
</html>"""


cli.add_command(create)
cli.add_command(build)
cli.add_command(post)
cli.add_command(eject)

if __name__ == "__main__":
    cli()
