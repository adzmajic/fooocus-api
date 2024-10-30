"""
Image process utils. Used to verify, convert and store Images.

@file: img_utils.py
@author: Konie
@update: 2024-03-23
"""
import base64
from io import BytesIO
from fastapi import UploadFile
from PIL import Image

import requests
import numpy as np


def upload2base64(image: UploadFile) -> str | None:
    """
    Convert UploadFile obj to base64 string
    Args:
        image (UploadFile): UploadFile obj
    Returns:
        str: base64 string, None for None
    """
    if image is None:
        return None
    image_bytes = image.file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return image_base64


def narray_to_base64img(narray: np.ndarray) -> str | None:
    """
    Convert numpy array to base64 image string.
    Args:
        narray: numpy array
    Returns:
        base64 image string
    """
    if narray is None:
        return None

    img = Image.fromarray(narray)
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode('utf-8')
    return base64_str


def narray_to_bytesimg(narray) -> bytes | None:
    """
    Convert numpy array to bytes image.
    Args:
        narray: numpy array
    Returns:
        bytes image
    """
    if narray is None:
        return None

    img = Image.fromarray(narray)
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    return byte_data


def read_input_image(input_image: UploadFile | str | None) -> np.ndarray | None:
    """
    Read input image from UploadFile or base64 string.
    Args:
        input_image: UploadFile, or base64 image string, or None
    Returns:
        numpy array of image
    """
    if input_image is None or input_image == '':
        return None
    if isinstance(input_image, str):
        input_image_bytes = base64.b64decode(input_image)
    else:
        input_image_bytes = input_image.file.read()
    pil_image = Image.open(BytesIO(input_image_bytes))
    image = np.array(pil_image)
    return image


def base64_to_stream(image: str) -> UploadFile | None:
    """
    Convert base64 image string to UploadFile.
    Args:
        image: base64 image string
    Returns:
        UploadFile or None
    """
    if image == '':
        return None
    if image.startswith('http'):
        return get_check_image(url=image)
    if image.startswith('data:image'):
        image = image.split(sep=',', maxsplit=1)[1]
    image_bytes = base64.b64decode(image)
    byte_stream = BytesIO()
    byte_stream.write(image_bytes)
    byte_stream.seek(0)
    return UploadFile(file=byte_stream)


def get_check_image(url: str) -> UploadFile | None:
    """
    Get image from url and check if it's valid.
    Args:
        url: image url
    Returns:
        UploadFile or None
    """
    if url == '':
        return None
    try:
        response = requests.get(url, timeout=10)
        binary_image = response.content
    except Exception:
        return None
    try:
        buffer = BytesIO(binary_image)
        Image.open(buffer)
    except Exception:
        return None
    byte_stream = BytesIO()
    byte_stream.write(binary_image)
    byte_stream.seek(0)
    return UploadFile(file=byte_stream)


def bytes_image_to_io(binary_image: bytes) -> BytesIO | None:
    """
    Convert bytes image to BytesIO.
    Args:
        binary_image: bytes image
    Returns:
        BytesIO or None
    """
    try:
        buffer = BytesIO(binary_image)
        Image.open(buffer)
    except Exception:
        return None
    byte_stream = BytesIO()
    byte_stream.write(binary_image)
    byte_stream.seek(0)
    return byte_stream


def bytes_to_base64img(byte_data: bytes) -> str | None:
    """
    Convert bytes image to base64 image string.
    Args:
        byte_data: bytes image
    Returns:
        base64 image string or None
    """
    if byte_data is None:
        return None

    base64_str = base64.b64encode(byte_data).decode('utf-8')
    return base64_str


def base64_to_bytesimg(base64_str: str) -> bytes | None:
    """
    Convert base64 image string to bytes image.
    Args:
        base64_str: base64 image string
    Returns:
        bytes image or None
    """
    if base64_str == '':
        return None
    bytes_image = base64.b64decode(base64_str)
    return bytes_image


def base64_to_narray(base64_str: str) -> np.ndarray | None:
    """
    Convert base64 image string to numpy array.
    Args:
        base64_str: base64 image string
    Returns:
        numpy array or None
    """
    if base64_str == '':
        return None
    bytes_image = base64.b64decode(base64_str)
    image = np.frombuffer(bytes_image, np.uint8)
    return image
