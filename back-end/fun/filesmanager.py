from logging import basicConfig, INFO, info, error

basicConfig(level=INFO)


class FileSplitter:
    def __init__(self, data, chunk_size_mb):
        self.data = data
        self.chunk_size_mb = chunk_size_mb
        self.chunk_size_bytes = chunk_size_mb * 1024 * 1024

    def split_data(self):
        try:
            chunk_data_list = []
            offset = 0

            while offset < len(self.data):
                chunk_data = self.data[offset:offset + self.chunk_size_bytes]
                if not chunk_data:
                    break
                chunk_data_list.append(chunk_data)
                offset += self.chunk_size_bytes

            info("split data done")
            return chunk_data_list
        except Exception as e:
            error(f"split data error caused by: {e}")
            return None


class FileMerger:
    def __init__(self, chunk_data_list):
        self.chunk_data_list = chunk_data_list
        self.output_data = b""

    def merge_data(self):
        try:
            self.output_data = "".join(self.chunk_data_list)
            return self.output_data
        except Exception as e:
            error(f"merge data error caused by: {e}")

