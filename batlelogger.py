import json
import os
import sys
import datetime as dt

import copyhelpers as cp_helper


class LogRecord:
    fmt = "{dttm}|{device_id}|{fraction_id}|{event}"

    def set(self, device_id, fraction_id, event, dttm):
        self.device_id = device_id
        self.fraction_id = fraction_id
        self.event = event
        self.dttm = dttm
    
    def __str__(self):
        return self.fmt.format(
            dttm=self.dttm.isoformat(),
            device_id=self.device_id,
            fraction_id=self.fraction_id,
            event=self.event
        )


class BattleLogger:
    line_terminator = "\n"
    mode = "a"

    def __init__(
        self,
        device_id,
        data_folder="/battle_log",
        backups_storage=None,
        encoding="UTF-8",
        rtc_instance=None,
        tzinfo=None,
        debug=True
    ):
        self.rtc_instance = rtc_instance
        self.tzinfo = tzinfo
        self.encoding = encoding
        self.backups_storage = backups_storage
        self.data_folder = data_folder
        self.device_id = device_id
        self.debug = debug
        
        self.record = LogRecord()
        self.metastore = os.path.join(self.data_folder, "metastore")
        
        if not os.path.exists(self.data_folder):
            os.mkdir(self.data_folder)
        if (
            os.path.exists(self.metastore)
            and self.check_file_not_empty(self.metastore)
        ):
            with open(self.metastore, "r") as f:
                battle_log_metadata = json.load(f)
            last_round_metadata = battle_log_metadata[-1]
        else:
            battle_log_metadata = list()
            last_round_metadata = {
                "id": 0,
                "start_dttm": None,
                "log_file": None
            }
        last_round_id = last_round_metadata["id"]
        self.round_id = last_round_id + 1
        self.round_start_dttm = self.get_dttm()
        log_filename = self.get_log_filename()
        self.round_log_path = os.path.join(self.data_folder, log_filename)
        battle_log_metadata.append(
            {
                "id": self.round_id,
                "start_dttm": self.round_start_dttm.isoformat(),
                "log_file": self.round_log_path
            }
        )
        with open(self.metastore, "w") as f:
            json.dump(battle_log_metadata, f)
        self.log("system", "Battle log started")
        self.save_backup()
        
    @staticmethod
    def check_file_not_empty(path):
        with open(path, "rb") as f:
            content = f.read(10)
        return len(content) == 10

    def get_dttm(self):
        if self.rtc_instance is None:
            return dt.datetime.now(tz=self.tzinfo)
        else:
            return self.rtc_instance.datetime
        
    def get_log_filename(self):
        return f"round_{self.round_id}__ts_{int(self.round_start_dttm.timestamp())}"
        
    def write_to_stdout(self, record):
        try:
            sys.stdout.write(str(record) + self.line_terminator)
        except:
            if hasattr(sys.stdout, "flush"):
                sys.stdout.flush()
                
    def write(self, record):
        with open(self.round_log_path, self.mode, encoding=self.encoding) as f:
            f.write(str(record) + self.line_terminator)
        
    def emit(self, record):
        if self.debug:
            self.write_to_stdout(record)
        self.write(record)

    def log(self, fraction_id, event):
        self.record.set(
            device_id=self.device_id,
            dttm=self.get_dttm(),
            fraction_id=fraction_id,
            event=event
            
        )
        self.emit(self.record)
            
    def save_backup(self):
        self.last_backup_dttm = self.get_dttm()
        if self.backups_storage is not None:
            backup_folder = os.path.join(
                self.backups_storage,
                str(int(self.last_backup_dttm.timestamp()))
            )
            if not os.path.exists(backup_folder):
                os.mkdir(backup_folder)
            bk_metastore = os.path.join(backup_folder, "metastore")
            bk_log = os.path.join(backup_folder, self.get_log_filename())
            cp_helper.copy_file(self.metastore, bk_metastore)
            cp_helper.copy_file(self.round_log_path, bk_log)
        
    def end(self):
        self.log("system", "Battle log finished")
        self.save_backup()
