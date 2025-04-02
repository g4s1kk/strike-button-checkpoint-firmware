import json
import os
import sys
import datetime as dt

import upysh


class LogRecord:
    fmt = "{dttm}|{device_id}|{faction_id}|{event}"

    def set(self, device_id, faction_id, event, dttm):
        self.device_id = device_id
        self.faction_id = faction_id
        self.event = event
        self.dttm = dttm

    def __str__(self):
        return self.fmt.format(
            dttm=self.dttm.isoformat(),
            device_id=self.device_id,
            faction_id=self.faction_id,
            event=self.event
        )


class BattleLogger:
    line_terminator = "\n"
    mode = "a"

    def __init__(
        self,
        device_id,
        data_folder="/battle_log",
        external_storage=None,
        encoding="UTF-8",
        rtc_instance=None,
        tzinfo=None,
        debug=True
    ):
        self.rtc_instance = rtc_instance
        self.tzinfo = tzinfo
        self.encoding = encoding
        self.device_id = device_id
        self.debug = debug
        self.buf = list()

        self.record = LogRecord()

        if not os.path.exists(data_folder):
            os.mkdir(data_folder)
        if external_storage is not None:
            ext_data_folder = os.path.join(
                external_storage,
                os.path.basename(data_folder)
            )
            if not os.path.exists(ext_data_folder):
                os.mkdir(ext_data_folder)
            self.ext_log_file = self.get_log_filename(
                dir=ext_data_folder
            )
        else:
            self.ext_log_file = None
        
        self.log_file = self.get_log_filename(
            dir=data_folder
        )
        self.log("system", "Battle log initialized")

    def get_filename_from_ts(self):
        ts = self.rtc_instance.datetime
        return str(int(ts.timestamp())) + ".log"

    def get_log_filename(self, dir):
        return os.path.join(
            dir,
            self.get_filename_from_ts()
        )

    def get_dttm(self):
        if self.rtc_instance is None:
            return dt.datetime.now(tz=self.tzinfo)
        else:
            return self.rtc_instance.datetime
        
    def write_to_buf(self, content):
        self.buf.append(content)

    def write_to_stdout(self, content):
        try:
            sys.stdout.write(content)
        except:
            if hasattr(sys.stdout, "flush"):
                sys.stdout.flush()

    def write_to_file(self, content, log_file):
        with open(log_file, self.mode, encoding=self.encoding) as f:
            f.write(content)

    def emit(self, record):
        content = str(record) + self.line_terminator
        if self.debug:
            self.write_to_stdout(content)
        self.write_to_buf(content)
        if self.ext_log_file is not None:
            self.write_to_file(content, self.ext_log_file)

    def log(self, faction_id, event):
        self.record.set(
            device_id=self.device_id,
            dttm=self.get_dttm(),
            faction_id=faction_id,
            event=event

        )
        self.emit(self.record)

    def flush_buf(self):
        with open(self.log_file, "w", encoding=self.encoding) as f:
            for line in self.buf:
                f.write(str(line) + self.line_terminator)
