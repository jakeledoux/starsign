from PIL import Image
import qrcode
from qrcode.image.pil import PilImage
from qrcode.image.pure import PymagingImage
from qrcode.image.svg import SvgPathImage
from typing import Dict, Optional
import urllib.parse

stellar_logo = Image.open('stellar_logo.png')


def encode_uri(operation: str, **kwargs: Dict[str, Optional[str]]) -> str:
    ''' https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0007.md
    '''
    base_uri = f'web+stellar:{operation}?'
    params = {key: value for key, value in kwargs.items() if value is not None}
    # Encode param dictionary into URL parameter string
    param_str = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    return base_uri + param_str


def request_payment(destination: str, amount: Optional[str] = None,
                    asset_code: Optional[str] = None,
                    asset_issuer: Optional[str] = None,
                    memo: Optional[str] = None,
                    memo_type: Optional[str] = None,
                    callback: Optional[str] = None,
                    msg: Optional[str] = None) -> str:
    ''' https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0007.md#operation-pay
    '''

    return encode_uri('pay', destination=destination, amount=amount,
                      asset_code=asset_code, asset_issuer=asset_issuer,
                      memo=memo, memo_type=memo_type, callback=callback,
                      msg=msg)


def make_qr(uri: str) \
        -> qrcode.QRCode:
    ''' Creates a QR code from URI.
    '''

    qr = qrcode.QRCode()
    qr.add_data(uri)
    qr.make(fit=True)

    return qr


def make_image(qr, type='png', write=False, filename=None, logo=False,
               logo_size=110):
    if type == 'png':
        if logo:
            factory = PilImage
        else:
            factory = PymagingImage
    elif logo:
        raise ValueError(f'Logo insertion unavailable with type: {type}')
    elif type == 'svg':
        factory = SvgPathImage
    else:
        raise ValueError(f'Invalid image type: {type}')

    img = qr.make_image(image_factory=factory)

    # Composite logo
    if logo:
        # Convert QR code to grayscale from mono
        img = img.convert('L')

        # Resize and composite logo image
        width, height = img.size
        resized_logo = stellar_logo.copy().resize((logo_size, logo_size),
                                                  Image.ANTIALIAS)
        box = (width // 2 - logo_size // 2,
               height // 2 - logo_size // 2)
        img.paste(resized_logo, box)

    # Save img
    if write:
        with open(filename or f'output.{type}', 'wb') as f:
            img.save(f)

    return img


if __name__ == '__main__':
    uri  = request_payment(
        'GBCOKLTKFJRR45RJBA336OE3ACKMFCLSODLHP6TTTNFVHVPXU7TW5U7F',
        amount=10, memo='Just a tip :)'
    )
    qr = make_qr(uri)
    img = make_image(qr, logo=True, write=True)
