from base64 import b64encode
from io import BytesIO

import requests
from PIL import Image
from flask import current_app

from app import db, models

_THUMB_WIDTH = 250


def thumb(cat: models.Cat) -> str:
    """Return thumbnail for cat image for further use in `data:image/png;base64,...`
    Args:
        cat (models.Cat): Cat object.
    Returns:
        Base64-encoded thumbnail in PNG format.
    """
    ret = cat.url
    # https://ia.wampi.ru/2020/09/26/x_0Baq_AkQY.th.jpg <- '.th' added to original URI
    if '.wampi.ru/' in ret:
        ret = ret[:-4] + '.th' + ret[-4:]
    else:
        th = models.Thumbnail.query.filter(models.Thumbnail.cat_id == cat.id).first()
        if th:
            if th.width != _THUMB_WIDTH:  # use only one size for thumbnails
                db.session.delete(th)
                db.session.commit()
                th = None
        if not th:
            th = models.Thumbnail(cat_id=cat.id,
                                  data=create_thumbnail_for_url(cat.url, _THUMB_WIDTH),
                                  width=_THUMB_WIDTH)
            db.session.add(th)
            db.session.commit()
        ret = 'data:image/png;base64,' + b64encode(th.data).decode()

    return ret


def create_thumbnail_for_url(url: str, size: int) -> bytes:
    """Create thumbnail for image.
    Args:
        url (str): Image URL.
        size (int): Thumbnail size.
    Returns:
        Output data (thumbnail bytes).
    """
    current_app.logger.debug(f'Downloading {url} to create thumbnail (w={size})')
    r = requests.get(url)
    if r.status_code == 200:
        data = create_thumbnail(r.content, size)
        if data:
            current_app.logger.info(f'Thumbnail (w={size}) for {url} created')
            return data


def create_thumbnail(in_data: bytes, size: int) -> bytes:
    """Create thumbnail for image bytes.
    Args:
        in_data (bytes): Input data (image bytes).
        size (int): Thumbnail size.
    Returns:
        Output data (thumbnail bytes).
    """
    if in_data:
        infile = BytesIO(in_data)

        img = Image.open(infile)
        img.thumbnail((size, 600 * size))

        out_file = BytesIO()
        img.save(out_file, 'png')
        out_data = out_file.getvalue()

        return out_data

# TODO look at https://www.cloudimage.io/en/home
