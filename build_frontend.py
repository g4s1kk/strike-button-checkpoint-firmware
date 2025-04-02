import flet as ft
import json

from src.config import config as cfg


def main(page: ft.Page):
    page.title = "Microdot Admin Panel"
    page.vertical_alignment = "center"
    
    # Состояние (ответы от бэка)
    log_output = ft.Text("Здесь будет отчёт...", selectable=True)
    upload_status = ft.Text()
    
    # 1. Кнопка "Просмотр отчёта" (запрос по WS)
    async def view_report(e):
        async with websockets.connect("ws://localhost:8000/ws") as ws:
            await ws.send(json.dumps({"action": "get_report"}))
            response = await ws.recv()
            log_output.value = response
            page.update()
    
    # 2. Кнопка "Скачать лог" (обычный HTTP-запрос)
    async def download_log(e):
        page.launch_url("http://localhost:8000/download_log")
    
    # 3. Кнопка "Загрузить конфиг" (отправка файла)
    async def upload_config(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        await file_picker.pick_files()
        
        if file_picker.result:
            file = file_picker.result.files[0]
            async with websockets.connect("ws://localhost:8000/ws") as ws:
                await ws.send(json.dumps({
                    "action": "upload_config",
                    "name": file.name,
                    "content": open(file.path).read()
                }))
                upload_status.value = "Конфиг загружен!"
                page.update()
    
    # Интерфейс
    page.add(
        ft.Column([
            ft.ElevatedButton("Просмотр отчёта", on_click=view_report),
            ft.ElevatedButton("Скачать лог", on_click=download_log),
            ft.ElevatedButton("Загрузить конфиг", on_click=upload_config),
            log_output,
            upload_status
        ])
    )

# Собираем фронт в HTML (для Microdot)
ft.app(target=main, view=None, port=cfg.WEB_PORT, export_path=cfg.WEB_MAIN_PATH)
