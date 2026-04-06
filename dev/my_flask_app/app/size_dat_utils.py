LEADER_FOLLOW_ROWS = [
    ["10", "10", "-1", "0", "1", "0"],
    ["20", "20", "0", "-1", "0", "1"],
]


def build_dat_line(row):
    return " ".join(str(item) for item in row)


def is_checked(value):
    return str(value).strip().lower() in {"1", "on", "true", "yes"}


def insert_leader_follow_rows(drawing_rows, enabled):
    if not enabled:
        return drawing_rows

    leader_follow_lines = [build_dat_line(row) for row in LEADER_FOLLOW_ROWS]
    drawing_lines = [build_dat_line(row) for row in drawing_rows]
    if drawing_lines[: len(leader_follow_lines)] == leader_follow_lines:
        return drawing_rows
    if all(line in drawing_lines for line in leader_follow_lines):
        return drawing_rows
    return LEADER_FOLLOW_ROWS + drawing_rows
