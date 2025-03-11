import subprocess

BYTES_IN_GB = 1024 ** 3
BYTES_IN_MB = 1024 ** 2

def parse_size(size_str):
    try:
        if size_str[-1].isalpha():
            unit = size_str[-1].upper()
            number = float(size_str[:-1])
            if unit == 'K':
                return int(number * 1024)
            elif unit == 'M':
                return int(number * (1024**2))
            elif unit == 'G':
                return int(number * (1024**3))
            elif unit == 'T':
                return int(number * (1024**4))
            elif unit == 'P':
                return int(number * (1024**5))
            else:
                return int(number)
        else:
            return int(size_str)
    except Exception:
        return None

def format_size(bytes_value):
    if bytes_value < BYTES_IN_GB:
        size_mb = bytes_value / BYTES_IN_MB
        return f"{size_mb:.2f}M"
    else:
        size_gb = bytes_value / BYTES_IN_GB
        return f"{size_gb:.2f}GB"

def get_free_space_for_device(device_path):
    df_cmd = ["df", "-B1", device_path]
    try:
        df_out = subprocess.check_output(df_cmd, universal_newlines=True).strip().split("\n")
        if len(df_out) >= 2:
            df_data = df_out[1].split()
            available_bytes = int(df_data[3])
            return available_bytes
    except Exception:
        return 0

def get_storage_info():
    cmd_lsblk_top = ["lsblk", "-r", "-n", "-d", "-o", "NAME,TYPE,SIZE"]
    lsblk_output_top = subprocess.check_output(cmd_lsblk_top, universal_newlines=True).strip().split("\n")
    devices = []
    for line in lsblk_output_top:
        parts = line.split()
        if len(parts) >= 3:
            dev_name = parts[0]
            dev_type = parts[1]
            dev_size = parts[2]
            if dev_type == "disk":
                devices.append((dev_name, dev_size))
    
    storage_info = []
    for (dev_name, dev_size) in devices:
        path = f"/dev/{dev_name}"
        cmd_lsblk_part = ["lsblk", "-r", "-n", path, "-o", "NAME,MOUNTPOINT,TYPE"]
        part_output = subprocess.check_output(cmd_lsblk_part, universal_newlines=True).strip().split("\n")
        free_space_bytes = 0
        found_partition = False
        for p_line in part_output:
            if not p_line.strip():
                continue
            p_parts = p_line.split()
            if len(p_parts) == 3:
                part_name, mountpoint, p_type = p_parts
                if p_type == "part" and mountpoint != "-":
                    found_partition = True
                    df_cmd = ["df", "-B1", f"/dev/{part_name}"]
                    try:
                        df_out = subprocess.check_output(df_cmd, universal_newlines=True).strip().split("\n")
                        if len(df_out) >= 2:
                            df_data = df_out[1].split()
                            available_bytes = int(df_data[3])
                            free_space_bytes += available_bytes
                    except Exception:
                        pass
        if not found_partition:
            free_space_bytes = get_free_space_for_device(path)
            
        total_size_bytes = parse_size(dev_size)
        total_size_str = format_size(total_size_bytes) if total_size_bytes is not None else dev_size
        free_space_str = format_size(free_space_bytes)
        storage_info.append({
            "path": path,
            "total_size": total_size_str,
            "free_space": free_space_str
        })

    return storage_info

def main():
    info = get_storage_info()
    for device in info:
        print("Device Path : ", device["path"])
        print("Total Size  : ", device["total_size"])
        print("Free Space  : ", device["free_space"])
        print("-" * 30)

if __name__ == "__main__":
    main()
