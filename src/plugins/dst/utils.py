def safe_get(lst: list, index: int):
    if 0 <= index < len(lst):
        return lst[index]
    else:
        return None

def copy_non_empty_fields(src, dest, key_set: set):
    for key, value in src.__dict__.items():
        if key not in key_set:
            continue
        if value is not None:
            setattr(dest, key, value)