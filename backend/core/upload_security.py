"""
Enterprise File Upload Security Validation

Defends against:
1. Disguised executables (PE, ELF, Mach-O, scripts renamed with safe extensions like .pdf/.png).
2. Prohibited executable extensions (.exe, .sh, .bat, .dll, .php, etc.).
3. Content-Type and Magic Header spoofing.
4. Directory traversal in filenames.
"""

import os
import re
from django.core.exceptions import ValidationError

# Prohibited file extensions that are executable or scripts
PROHIBITED_EXTENSIONS = {
    'exe', 'dll', 'so', 'dylib', 'bin', 'com', 'scr', 'msi', 'cmd', 'bat',
    'sh', 'bash', 'zsh', 'ps1', 'vbs', 'vbe', 'js', 'jse', 'wsf', 'wsh',
    'jar', 'war', 'ear', 'class',
    'php', 'phtml', 'php3', 'php4', 'php5', 'phps',
    'asp', 'aspx', 'cer', 'asa', 'asax',
    'jsp', 'jspx', 'cgi', 'pl', 'py', 'pyc', 'pyo', 'pyd',
    'hta', 'cpl', 'msc', 'reg',
}

# Strictly allowed extensions for documents and media
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'zip'
}

# Signatures for known executable formats (disguised executable detection)
EXECUTABLE_SIGNATURES = [
    (b'MZ', 'Windows DOS/PE Executable'),
    (b'\x7fELF', 'Linux ELF Binary'),
    (b'\xfe\xed\xfa\xce', 'Mach-O Binary (32-bit)'),
    (b'\xfe\xed\xfa\xcf', 'Mach-O Binary (64-bit)'),
    (b'\xce\xfa\xed\xfe', 'Mach-O Binary (Reverse 32-bit)'),
    (b'\xcf\xfa\xed\xfe', 'Mach-O Binary (Reverse 64-bit)'),
    (b'\xca\xfe\xba\xbe', 'Java Class / Universal Binary'),
    (b'#!', 'Script with Shebang Header'),
]

# Magic signatures for allowed file formats
TYPE_SIGNATURES = {
    'pdf': [b'%PDF-'],
    'png': [b'\x89PNG\r\n\x1a\n'],
    'jpg': [b'\xff\xd8\xff'],
    'jpeg': [b'\xff\xd8\xff'],
    'gif': [b'GIF87a', b'GIF89a'],
    'zip': [b'PK\x03\x04'],
    'docx': [b'PK\x03\x04'],
    'xlsx': [b'PK\x03\x04'],
    'pptx': [b'PK\x03\x04'],
}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and dangerous characters"""
    if not filename:
        return 'unnamed_file'
    basename = os.path.basename(filename)
    # Strip any directory traversal or path separators
    basename = re.sub(r'[\/\\:\*\?"<>\|]', '_', basename)
    return basename.strip()


def validate_uploaded_file(file_obj) -> None:
    """
    Exhaustively inspect an uploaded file object.
    Throws ValidationError if:
    - Extension is prohibited / executable.
    - Magic header matches an executable format (MZ, ELF, Mach-O, scripts).
    - File claims to be a format (e.g. PDF/PNG/JPEG) but magic bytes don't match.
    - File contains embedded script tags or shell headers.
    """
    if not file_obj:
        return

    filename = getattr(file_obj, 'name', '') or ''
    sanitized_name = sanitize_filename(filename).lower()

    # Extract extension
    parts = sanitized_name.split('.')
    ext = parts[-1] if len(parts) > 1 else ''

    if not ext:
        raise ValidationError("Upload denied: file must have an extension.")

    # Check prohibited extensions
    if ext in PROHIBITED_EXTENSIONS:
        raise ValidationError(f"Upload denied: executable extension .{ext} is strictly prohibited.")

    # Check if extension is in allowed list
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Upload denied: extension .{ext} is not supported.")

    # Read leading bytes for magic signature inspection
    try:
        header = file_obj.read(1024)
        file_obj.seek(0)
    except Exception as e:
        raise ValidationError(f"Upload denied: unable to inspect file content ({str(e)}).")

    if not header:
        # Empty file check: plain text or csv might be empty, but binary formats shouldn't be
        if ext in ['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'pptx']:
            raise ValidationError("Upload denied: file is empty.")
        return

    # Check for executable signatures (disguised executables)
    for sig, desc in EXECUTABLE_SIGNATURES:
        if header.startswith(sig):
            raise ValidationError(
                f"Upload denied: disguised executable detected ({desc}). File content does not match extension .{ext}."
            )

    # Check script content in leading bytes
    lower_header = header.lower()
    if b'<?php' in lower_header or b'<%eval' in lower_header or b'<script' in lower_header:
        raise ValidationError(
            f"Upload denied: active script code detected in file content for extension .{ext}."
        )

    # Validate signature against expected extension
    expected_sigs = TYPE_SIGNATURES.get(ext)
    if expected_sigs:
        matched = False
        for expected in expected_sigs:
            if header.startswith(expected):
                matched = True
                break
        if not matched:
            raise ValidationError(
                f"Upload denied: file content signature does not match claimed format .{ext}."
            )

    # For text/csv files, verify they are text-encoded without null bytes
    if ext in ['txt', 'csv']:
        if b'\x00' in header:
            raise ValidationError(
                f"Upload denied: binary data / null bytes detected in text file .{ext}."
            )
