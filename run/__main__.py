from datetime import datetime
import typing
import typer
import commands.sdk as sdk
import commands.docs as docs
import commands.utils as utils

app = typer.Typer()
app.add_typer(
    docs.docs, name="docs", help="Generate documentation based on carriers metadata."
)


@app.command()
def add_extension(
    id: str = typer.Option(..., prompt=True),
    name: str = typer.Option(..., prompt=True),
    features: typing.Optional[str] = typer.Option(
        ", ".join(utils.DEFAULT_FEATURES), prompt=True
    ),
    version: typing.Optional[str] = typer.Option(
        f"{datetime.now().strftime('%Y.%-m')}", prompt=True
    ),
    is_xml_api: typing.Optional[bool] = typer.Option(..., prompt="Is XML API?"),
):
    sdk.add_extension(
        id,
        name,
        features,
        version,
        is_xml_api,
    )


@app.command()
def add_features(extension: str = typer.Option(None)):
    if not extension:
        print("No carrier slug provided")
        raise typer.Abort()

    _features = typer.prompt(
        "Carrier features (default: tracking, rating, shipping, pickup, address, upload)"
    )

    sdk.add_features(
        extension,
        _features,
    )


if __name__ == "__main__":
    app()
