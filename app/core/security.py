import re
import string
import unicodedata

def _get_default_allowed_extensions():
    return [
        ".txt",
        ".pdf",
        ".docx",
        ".doc",
    ]

def _get_default_allowed_content_types():
    return [
        "text/plain",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

def _get_dangerous_extensions():
    return [
        ".exe",
        ".bat",
        ".cmd",
        ".sh",
        ".ps1",
        ".vbs",
        ".scr",
        ".com",
        ".pif",
        ".app",
        ".jar",
        ".msi"
    ]

def _get_dangerous_content_types():
    return [
        "application/x-executable",
        "application/x-msdownload",
        "application/x-sh",
        "application/x-bat",
        "application/x-msi",
        "applicattion/octet-stream"
    ]

def _check_filename_security(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename or "\x00" in filename:
        return False, "Invalid filename deteted"
    return True, ""

def validate_file_upload(
    filename: str,
    content_type: str | None,
    file_size: int | None = None,
    max_size: int = 10 * 1024 * 1024, # 10MB default
    allowed_extensions: list[str] | None = None,
    allowed_content_types: list[str] | None = None
):
    if not allowed_extensions:
        allowed_extensions = _get_default_allowed_extensions()
    if not allowed_content_types:
        allowed_content_types = _get_default_allowed_content_types()

    dangerous_extensions = _get_dangerous_extensions()
    dangerous_content_types = _get_dangerous_content_types()


    is_valid, error = _check_filename_security(filename=filename)
    if not is_valid:
        return is_valid, error

    if file_size and file_size > max_size:
        return False, f"File size exceeds maximum allowed size of {max_size} bytes"

    file_ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if not file_ext:
        return False, ""

    if file_ext in dangerous_extensions or file_ext not in allowed_extensions:
        return (
            False,
            f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    if not content_type:
        return True, ""

    if content_type in dangerous_content_types:
        return False, "Invalid file content type"

    if content_type not in allowed_content_types:
        return False, "Invalid file content type"

    return True, ""

def sanitise_filename(filename: str, max_length: int = 256):
    filename = filename.replace("\x00", "")
    filename = filename.replace("/", "_")
    filename = filename.replace("\\", "_")

    # remove all leading dots and path traversal patterns
    filename = re.sub(r"^\.*", "", filename)
    filename = re.sub(r"\.\._*", "_", filename)

    # Replace special characters
    unsafe_chars = '<>:"|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")

    filename = re.sub(r" +", "_", filename)

    def is_safe_char(c):
        if c in string.ascii_letters:
            return True

        if unicodedata.category(c)[0] == "L":
            return True
        return False

    sanitised = "".join(c if is_safe_char(c) else "_" for c in filename)

    parts = sanitised.rsplit(".", 1)
    if len(parts) == 2:
        name, ext = parts
        name = name.lstrip("-.")
        if name:
            sanitised = f"{name}.{ext}"
        else:
            sanitised = f"file.{ext}"
    else:
        sanitised = sanitised.strip("_.")

    if not sanitised or sanitised == ".":
        sanitised = "file"

    if len(sanitised) > max_length:
        if "." in sanitised:
            name, ext = sanitised.rsplit(".", 1)

            max_name_length = max_length - len(ext) - 1
            if max_name_length > 0:
                sanitised = f"{name[:max_name_length]}.{ext}"
            else:
                sanitised = sanitised[:max_length]
        else:
            sanitised = sanitised[:max_length]

    return sanitised