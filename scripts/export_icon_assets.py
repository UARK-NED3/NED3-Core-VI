"""Export padded icon-only PNGs from approved primary-lockup rasters.

The Core VI source artwork is raster. This helper makes a deterministic
downloadable icon crop without redrawing or restyling the approved mark.
"""

from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1] / "assets"


def nonwhite_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    """Return the bounding box of non-white pixels in an RGBA image."""
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    difference = ImageChops.difference(image, background).convert("L")
    return difference.point(lambda value: 255 if value > 18 else 0).getbbox()


def export_icon(primary_path: Path) -> None:
    image = Image.open(primary_path).convert("RGBA")
    width, height = image.size

    # Approved primary lockups place the large icon in the upper-left region.
    # Excluding the lower reference icon avoids combining two different scales.
    source_region = image.crop((0, 0, round(width * 0.40), round(height * 0.72)))
    box = nonwhite_bbox(source_region)
    if box is None:
        raise RuntimeError(f"No icon pixels found in {primary_path}")

    icon = source_region.crop(box)
    pad = max(24, round(max(icon.size) * 0.12))
    canvas = Image.new("RGBA", (icon.width + 2 * pad, icon.height + 2 * pad), (255, 255, 255, 0))
    canvas.alpha_composite(icon, (pad, pad))
    canvas.save(primary_path.with_name("icon-color.png"), optimize=True)


def main() -> None:
    for primary in sorted(ROOT.glob("*/primary-light.png")):
        export_icon(primary)
        print(primary.parent.name)


if __name__ == "__main__":
    main()
