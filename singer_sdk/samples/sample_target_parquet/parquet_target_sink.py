"""Sample Parquet target stream class, which handles writing streams."""

from typing import Any, Dict, List, Tuple, Union

import pyarrow as pa
import pyarrow.parquet as pq

from singer_sdk.sinks import Sink
from singer_sdk.helpers._flattening import RecordFlattener

import pandas


class SampleParquetTargetSink(Sink):
    """Parquery target sample class."""

    DEFAULT_BATCH_SIZE_ROWS = 100000

    def drain(self, records_to_drain: Union[List[dict], Any]) -> None:
        """Write any prepped records out and return only once fully written."""
        # TODO: Replace with actual schema from the SCHEMA message
        schema = pa.schema([("some_int", pa.int32()), ("some_string", pa.string())])
        writer = pq.ParquetWriter(self.config["filepath"], schema)

        count = 0
        flattened_records = []
        flattener = RecordFlattener()
        for record in records_to_drain:
            flatten_record = flattener.flatten_record(record, schema, max_level=0)
            flattened_records.append(flatten_record)
            count += 1

        df = pandas.DataFrame(data=flattened_records)
        table = pa.Table.from_pandas(df)
        writer.write_table(table)
        writer.close()
        self.tally_record_written(count)

    @staticmethod
    def translate_data_type(singer_type: Union[str, Dict]) -> Any:
        """Translate from singer_type to a native type."""
        if singer_type in ["decimal", "float", "double"]:
            return pa.decimal128
        if singer_type in ["date-time"]:
            return pa.datetime
        if singer_type in ["date"]:
            return pa.date64
        return pa.string

    def _get_parquet_schema(self) -> List[Tuple[str, Any]]:
        col_list: List[Tuple[str, Any]] = []
        for property in self.schema["properties"]:
            col_list.append(
                (property["name"], self.translate_data_type(property["type"]))
            )
        return col_list
