def _read_csv_robust(self, file_path, max_rows=None):
    # 1) try pyarrow fast path (assumes comma delimiter)
    try:
        return pd.read_csv(
            file_path,
            engine="pyarrow",
            dtype_backend="pyarrow",
            na_values=['', ' ', 'NA', 'N/A', 'NULL', 'null', 'NaN', '-'],
            nrows=max_rows
        )
    except Exception:
        pass
    # 2) fall back to sniffed delimiter + tolerant encodings
    encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
    for enc in encodings:
        try:
            return pd.read_csv(
                file_path,
                sep=None, engine='python', encoding=enc,
                dtype_backend="numpy_nullable",
                na_values=['', ' ', 'NA', 'N/A', 'NULL', 'null', 'NaN', '-'],
                keep_default_na=True,
                on_bad_lines='skip',
                nrows=max_rows
            )
        except Exception:
            continue
    raise ValueError("Could not read CSV with pyarrow or common encodings/delimiters")
